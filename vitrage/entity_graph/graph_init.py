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
import threading
import time

from oslo_log import log
import oslo_messaging

from vitrage.common.constants import DatasourceAction
from vitrage.common.utils import spawn
from vitrage.entity_graph import datasource_rpc as ds_rpc
from vitrage.entity_graph import EVALUATOR_TOPIC
from vitrage.entity_graph.processor.processor import Processor
from vitrage.entity_graph.scheduler import Scheduler
from vitrage.entity_graph.workers import GraphWorkersManager
from vitrage import messaging

LOG = log.getLogger(__name__)


class VitrageGraphInit(object):
    def __init__(self, conf, graph, db_connection):
        self.conf = conf
        self.graph = graph
        self.db = db_connection
        self.workers = GraphWorkersManager(conf, graph, db_connection)
        self.events_coordination = EventsCoordination(
            conf,
            self.process_event,
            conf.datasources.notification_topic_collector,
            EVALUATOR_TOPIC)
        self.scheduler = Scheduler(conf, graph, self.events_coordination)
        self.processor = Processor(conf, graph, self.scheduler.graph_persistor)

    def run(self):
        LOG.info('Init Started')
        LOG.info('clearing database active_actions')
        self.db.active_actions.delete()
        ds_rpc.get_all(
            ds_rpc.create_rpc_client_instance(self.conf),
            self.events_coordination,
            self.conf.datasources.types,
            action=DatasourceAction.INIT_SNAPSHOT,
            retry_on_fault=True,
            first_call_timeout=10)
        self.processor.start_notifier()
        spawn(self.start_all_workers)
        self.workers.run()

    def start_all_workers(self):
        self.workers.submit_start_evaluations()  # evaluate entire graph
        self.graph.subscribe(self.workers.submit_graph_update)
        self.scheduler.start_periodic_tasks()
        LOG.info('Init Finished')
        self.events_coordination.start()

    def process_event(self, event):
        if event.get('template_action'):
            self.workers.submit_template_event(event)
            self.workers.submit_evaluators_reload_templates()
        else:
            self.processor.process_event(event)


PRIORITY_DELAY = 0.05


class EventsCoordination(object):
    def __init__(self, conf, do_work_func, topic_low, topic_high):
        self._conf = conf
        self._lock = threading.Lock()
        self._high_event_finish_time = 0

        def do_work(event):
            try:
                return do_work_func(event)
            except Exception:
                LOG.exception('Got Exception for event %s', str(event))

        self._do_work_func = do_work

        self._low_pri_listener = self._init_listener(
            topic_low, self._do_low_priority_work)
        self._high_pri_listener = self._init_listener(
            topic_high, self._do_high_priority_work)

    def start(self):
        LOG.info('Listening on %s', self._high_pri_listener.targets[0].topic)
        LOG.info('Listening on %s', self._low_pri_listener.targets[0].topic)
        self._high_pri_listener.start()
        self._low_pri_listener.start()

    def stop(self):
        self._low_pri_listener.stop()
        self._high_pri_listener.stop()

    def wait(self):
        self._low_pri_listener.wait()
        self._high_pri_listener.wait()

    def _do_high_priority_work(self, event):
        self._lock.acquire()
        self._do_work_func(event)
        self._high_event_finish_time = time.time()
        self._lock.release()

    def _do_low_priority_work(self, event):
        while True:
            self._lock.acquire()
            if (time.time() - self._high_event_finish_time) < PRIORITY_DELAY:
                self._lock.release()
                time.sleep(PRIORITY_DELAY)
            else:
                break
        self._do_work_func(event)
        self._lock.release()

    def handle_multiple_low_priority(self, events):
        for e in events:
            self._do_low_priority_work(e)

    def _init_listener(self, topic, callback):
        if not topic:
            return
        return messaging.get_notification_listener(
            transport=messaging.get_transport(self._conf),
            targets=[oslo_messaging.Target(topic=topic)],
            endpoints=[PushNotificationsEndpoint(callback)])


class PushNotificationsEndpoint(object):
    def __init__(self, process_event_callback):
        self.process_event_callback = process_event_callback

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        try:
            self.process_event_callback(payload)
        except Exception:
            LOG.exception('Failed to process event callback.')
