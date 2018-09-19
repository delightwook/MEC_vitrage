# Copyright 2018 - Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import abc
import cotyledon
import multiprocessing
from six.moves import _thread

from oslo_concurrency import processutils as ps
from oslo_log import log
import oslo_messaging

from vitrage.api_handler.apis.alarm import AlarmApis
from vitrage.api_handler.apis.event import EventApis
from vitrage.api_handler.apis.rca import RcaApis
from vitrage.api_handler.apis.resource import ResourceApis
from vitrage.api_handler.apis.template import TemplateApis
from vitrage.api_handler.apis.topology import TopologyApis
from vitrage.api_handler.apis.webhook import WebhookApis
from vitrage.common.constants import TemplateStatus as TStatus
from vitrage.common.constants import TemplateTypes as TType
from vitrage.common.exception import VitrageError
from vitrage.entity_graph import EVALUATOR_TOPIC
from vitrage.evaluator.actions.base import ActionMode
from vitrage.evaluator.scenario_evaluator import ScenarioEvaluator
from vitrage.evaluator.scenario_repository import ScenarioRepository
from vitrage import messaging
from vitrage import rpc as vitrage_rpc
from vitrage import storage

LOG = log.getLogger(__name__)

# Supported message types
GRAPH_UPDATE = 'graph_update'
START_EVALUATION = 'start_evaluation'
RELOAD_TEMPLATES = 'reload_templates'
TEMPLATE_ACTION = 'template_action'

ADD = 'add'
DELETE = 'delete'


class GraphWorkersManager(cotyledon.ServiceManager):
    """GraphWorkersManager

     - worker processes
     - the queues used to communicate with these workers
     - methods interface to submit tasks to workers
    """
    def __init__(self, conf, entity_graph, db):
        super(GraphWorkersManager, self).__init__()
        self._conf = conf
        self._entity_graph = entity_graph
        self._db = db
        self._evaluator_queues = []
        self._template_queues = []
        self._api_queues = []
        self._all_queues = []
        self.register_hooks(on_terminate=self._stop)
        self.add_evaluator_workers()
        self.add_template_workers()
        self.add_api_workers()

    def add_evaluator_workers(self):
        """Add evaluator workers

        Evaluator workers receive all graph updates, hence are updated.
        Each evaluator worker holds an enabled scenario-evaluator and process
        every change.
        Each worker's scenario-evaluator runs different template scenarios.
        Interface to these workers is:
        submit_graph_update(..)
        submit_start_evaluations(..)
        submit_evaluators_reload_templates(..)
        """
        if self._evaluator_queues:
            raise VitrageError('add_evaluator_workers called more than once')
        workers = self._conf.evaluator.workers or ps.get_worker_count()
        queues = [multiprocessing.JoinableQueue() for i in range(workers)]
        self.add(EvaluatorWorker,
                 args=(self._conf, queues, self._entity_graph, workers),
                 workers=workers)
        self._evaluator_queues = queues
        self._all_queues.extend(queues)

    def add_template_workers(self):
        """Add template workers

        Template workers receive all graph updates, hence are updated.
        Each template worker holds a disabled scenario-evaluator that does
        not process changes.
        The scenario-evaluator is enabled when a template add/delete arrives,
        so this worker will run the added template on the entire graph.
        Interface to these workers is:
        submit_graph_update(..)
        submit_template_event(..)
        """
        if self._template_queues:
            raise VitrageError('add_template_workers called more than once')
        workers = 1  # currently more than one worker is not supported
        queues = [multiprocessing.JoinableQueue() for i in range(workers)]
        self.add(TemplateLoaderWorker,
                 args=(self._conf, queues, self._entity_graph),
                 workers=workers)
        self._template_queues = queues
        self._all_queues.extend(queues)

    def add_api_workers(self):
        """Add Api workers

        Api workers receive all graph updates, hence are updated.
        Each template worker holds a disabled scenario-evaluator that does
        not process changes.
        These also hold a rpc server and process the incoming Api calls
        """
        if self._api_queues:
            raise VitrageError('add_api_workers called more than once')
        workers = self._conf.api.workers
        queues = [multiprocessing.JoinableQueue() for i in range(workers)]
        self.add(ApiWorker,
                 args=(self._conf, queues, self._entity_graph),
                 workers=workers)
        self._api_queues = queues
        self._all_queues.extend(queues)

    def submit_graph_update(self, before, current, is_vertex, *args, **kwargs):
        """Graph update all workers

        This method is subscribed to entity graph changes.
        Per each change in the main entity graph, this method will notify
         each of the workers, causing them to update their own graph.
        """
        self._submit_and_wait(
            self._all_queues,
            (GRAPH_UPDATE, before, current, is_vertex))

    def submit_start_evaluations(self):
        """Enable scenario-evaluator in all evaluator workers

        Enables the worker's scenario-evaluator, and run it on the entire graph
        """
        self._submit_and_wait(self._evaluator_queues, (START_EVALUATION,))

    def submit_evaluators_reload_templates(self):
        """Recreate the scenario-repository in all evaluator workers

        So that new/deleted templates are added/removed
        """
        self._submit_and_wait(self._evaluator_queues, (RELOAD_TEMPLATES,))

    def submit_template_event(self, event):
        """Template worker to load the new/deleted template

        Load the template to scenario-evaluator and run it on the entire graph
        """
        template_action = event.get(TEMPLATE_ACTION)

        if template_action == ADD:
            templates = self._db.templates.query(status=TStatus.LOADING)
            new_status = TStatus.ACTIVE
            action_mode = ActionMode.DO
        elif template_action == DELETE:
            templates = self._db.templates.query(status=TStatus.DELETING)
            new_status = TStatus.DELETED
            action_mode = ActionMode.UNDO
        else:
            raise VitrageError('Invalid template_action %s' % template_action)

        self._submit_and_wait(
            self._template_queues,
            (
                TEMPLATE_ACTION,
                [t.name for t in templates
                 if t.template_type == TType.STANDARD],
                action_mode,
            ))

        for t in templates:
            self._db.templates.update(t.uuid, 'status', new_status)

    @staticmethod
    def _submit_and_wait(queues, payload):
        for q in queues:
            q.put(payload)
        for q in queues:
            q.join()

    @staticmethod
    def _stop():
        # send SEGINT (instant exit) instead of SIGTERM
        _thread.interrupt_main()


class GraphCloneWorkerBase(cotyledon.Service):
    def __init__(self,
                 worker_id,
                 conf,
                 task_queues,
                 entity_graph):
        super(GraphCloneWorkerBase, self).__init__(worker_id)
        self._conf = conf
        self._task_queue = task_queues[worker_id]
        self._entity_graph = entity_graph

    name = 'GraphCloneWorkerBase'

    @abc.abstractmethod
    def _init_instance(self):
        """This method is executed in the newly created process"""
        raise NotImplementedError

    def run(self):
        LOG.info("%s - Starting %s", self.__class__.__name__, self.worker_id)
        self._entity_graph.notifier._subscriptions = []  # Quick n dirty
        self._init_instance()
        self._read_queue()

    def _read_queue(self):
        LOG.debug("%s - reading queue %s",
                  self.__class__.__name__, self.worker_id)
        while True:
            try:
                next_task = self._task_queue.get()
                self.do_task(next_task)
            except Exception:
                LOG.exception("Graph may not be in sync.")
            self._task_queue.task_done()

    def do_task(self, task):
        action = task[0]
        if action == GRAPH_UPDATE:
            (action, before, current, is_vertex) = task
            self._graph_update(before, current, is_vertex)

    def _graph_update(self, before, current, is_vertex):
        if current:
            if is_vertex:
                self._entity_graph.add_vertex(current)
            else:
                self._entity_graph.add_edge(current)
        else:
            if is_vertex:
                self._entity_graph.delete_vertex(before)
            else:
                self._entity_graph.delete_edge(before)


class EvaluatorWorker(GraphCloneWorkerBase):
    def __init__(self,
                 worker_id,
                 conf,
                 task_queues,
                 e_graph,
                 workers_num):
        super(EvaluatorWorker, self).__init__(
            worker_id, conf, task_queues, e_graph)
        self._workers_num = workers_num
        self._evaluator = None

    name = 'EvaluatorWorker'

    def _init_instance(self):
        scenario_repo = ScenarioRepository(self._conf, self.worker_id,
                                           self._workers_num)
        actions_callback = messaging.VitrageNotifier(
            conf=self._conf,
            publisher_id='vitrage_evaluator',
            topics=[EVALUATOR_TOPIC]).notify
        self._evaluator = ScenarioEvaluator(
            self._conf,
            self._entity_graph,
            scenario_repo,
            actions_callback,
            enabled=False)
        self._evaluator.scenario_repo.log_enabled_scenarios()

    def do_task(self, task):
        super(EvaluatorWorker, self).do_task(task)
        action = task[0]
        if action == START_EVALUATION:
            self._evaluator.run_evaluator()
        elif action == RELOAD_TEMPLATES:
            self._reload_templates()

    def _reload_templates(self):
        LOG.info("reloading evaluator scenarios")
        scenario_repo = ScenarioRepository(self._conf, self.worker_id,
                                           self._workers_num)
        self._evaluator.scenario_repo = scenario_repo
        self._evaluator.scenario_repo.log_enabled_scenarios()


class TemplateLoaderWorker(GraphCloneWorkerBase):
    def __init__(self,
                 worker_id,
                 conf,
                 task_queues,
                 e_graph):
        super(TemplateLoaderWorker, self).__init__(worker_id,
                                                   conf,
                                                   task_queues,
                                                   e_graph)
        self._evaluator = None

    name = 'TemplateLoaderWorker'

    def _init_instance(self):
        actions_callback = messaging.VitrageNotifier(
            conf=self._conf,
            publisher_id='vitrage_evaluator',
            topics=[EVALUATOR_TOPIC]).notify
        self._evaluator = ScenarioEvaluator(
            self._conf,
            self._entity_graph,
            None,
            actions_callback,
            enabled=False)

    def do_task(self, task):
        super(TemplateLoaderWorker, self).do_task(task)
        action = task[0]
        if action == TEMPLATE_ACTION:
            (action, template_names, action_mode) = task
            self._template_action(template_names, action_mode)

    def _template_action(self, template_names, action_mode):
        self._enable_evaluator_templates(template_names)
        self._evaluator.run_evaluator(action_mode)
        self._disable_evaluator()

    def _enable_evaluator_templates(self, template_names):
        scenario_repo = ScenarioRepository(self._conf)
        for s in scenario_repo._all_scenarios:
            s.enabled = False
            for template_name in template_names:
                if s.id.startswith(template_name):
                    s.enabled = True
        self._evaluator.scenario_repo = scenario_repo
        self._evaluator.scenario_repo.log_enabled_scenarios()
        self._evaluator.enabled = True

    def _disable_evaluator(self):
        self._entity_graph.notifier._subscriptions = []  # Quick n dirty
        self._evaluator.enabled = False


class ApiWorker(GraphCloneWorkerBase):

    name = 'ApiWorker'

    def _init_instance(self):
        conf = self._conf
        LOG.info("Vitrage Api Handler Service - Starting...")
        notifier = messaging.VitrageNotifier(conf, "vitrage.api",
                                             [EVALUATOR_TOPIC])
        db = storage.get_connection_from_config(conf)
        transport = messaging.get_rpc_transport(conf)
        rabbit_hosts = conf.oslo_messaging_rabbit.rabbit_hosts
        target = oslo_messaging.Target(topic=conf.rpc_topic,
                                       server=rabbit_hosts)

        endpoints = [TopologyApis(self._entity_graph, conf),
                     AlarmApis(self._entity_graph, conf),
                     RcaApis(self._entity_graph, conf),
                     TemplateApis(notifier, db),
                     EventApis(conf),
                     ResourceApis(self._entity_graph, conf),
                     WebhookApis(conf)]

        server = vitrage_rpc.get_server(target, endpoints, transport)

        server.start()

        LOG.info("Vitrage Api Handler Service - Started!")
