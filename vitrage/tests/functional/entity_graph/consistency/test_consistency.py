# Copyright 2016 - Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from datetime import timedelta
import time

from oslo_config import cfg
from six.moves import queue
from testtools import matchers

from vitrage.common.constants import EdgeLabel
from vitrage.common.constants import EntityCategory
from vitrage.common.constants import VertexProperties as VProps
from vitrage.datasources.nagios import NAGIOS_DATASOURCE
from vitrage.datasources.nova.host import NOVA_HOST_DATASOURCE
from vitrage.datasources.nova.instance import NOVA_INSTANCE_DATASOURCE
from vitrage.datasources.nova.zone import NOVA_ZONE_DATASOURCE
from vitrage.entity_graph.consistency.consistency_enforcer \
    import ConsistencyEnforcer
from vitrage.entity_graph.processor.processor import Processor
from vitrage.evaluator.scenario_evaluator import ScenarioEvaluator
from vitrage.evaluator.scenario_repository import ScenarioRepository
from vitrage.graph.driver.networkx_graph import NXGraph
import vitrage.graph.utils as graph_utils
from vitrage.tests.functional.base import TestFunctionalBase
from vitrage.tests.functional.test_configuration import TestConfiguration
from vitrage.tests.mocks import utils
from vitrage.utils.datetime import utcnow


class TestConsistencyFunctional(TestFunctionalBase, TestConfiguration):

    CONSISTENCY_OPTS = [
        cfg.IntOpt('min_time_to_delete',
                   default=1,
                   min=1),
        cfg.IntOpt('initialization_interval',
                   default=1,
                   min=1),
        cfg.IntOpt('initialization_max_retries',
                   default=10),
    ]

    EVALUATOR_OPTS = [
        cfg.StrOpt('templates_dir',
                   default=utils.get_resources_dir() +
                   '/templates/consistency',
                   ),
        cfg.StrOpt('equivalences_dir',
                   default='equivalences',
                   ),
        cfg.StrOpt('notifier_topic',
                   default='vitrage.evaluator',
                   ),
    ]

    # noinspection PyAttributeOutsideInit,PyPep8Naming
    @classmethod
    def setUpClass(cls):
        super(TestConsistencyFunctional, cls).setUpClass()
        cls.conf = cfg.ConfigOpts()
        cls.conf.register_opts(cls.CONSISTENCY_OPTS, group='consistency')
        cls.conf.register_opts(cls.PROCESSOR_OPTS, group='entity_graph')
        cls.conf.register_opts(cls.EVALUATOR_OPTS, group='evaluator')
        cls.conf.register_opts(cls.DATASOURCES_OPTS, group='datasources')
        cls.add_db(cls.conf)
        cls.load_datasources(cls.conf)
        cls.graph = NXGraph("Entity Graph")
        cls.processor = Processor(cls.conf, cls.graph)

        cls.event_queue = queue.Queue()

        def actions_callback(event_type, data):
            """Mock notify method

            Mocks vitrage.messaging.VitrageNotifier.notify(event_type, data)

            :param event_type: is currently always the same and is ignored
            :param data:
            """
            cls.event_queue.put(data)

        scenario_repo = ScenarioRepository(cls.conf)
        cls.evaluator = ScenarioEvaluator(cls.conf,
                                          cls.processor.entity_graph,
                                          scenario_repo,
                                          actions_callback)
        cls.consistency_enforcer = ConsistencyEnforcer(
            cls.conf,
            cls.processor.entity_graph,
            actions_callback)

    def test_periodic_process(self):
        # Setup
        consistency_interval = self.conf.datasources.snapshots_interval
        self._periodic_process_setup_stage(consistency_interval)

        # Action
        time.sleep(2 * consistency_interval + 1)
        self.consistency_enforcer.periodic_process()
        self._process_events()

        # Test Assertions
        instance_vertices = self.processor.entity_graph.get_vertices({
            VProps.VITRAGE_CATEGORY: EntityCategory.RESOURCE,
            VProps.VITRAGE_TYPE: NOVA_INSTANCE_DATASOURCE
        })
        deleted_instance_vertices = \
            self.processor.entity_graph.get_vertices({
                VProps.VITRAGE_CATEGORY: EntityCategory.RESOURCE,
                VProps.VITRAGE_TYPE: NOVA_INSTANCE_DATASOURCE,
                VProps.VITRAGE_IS_DELETED: True
            })
        self.assertThat(instance_vertices,
                        matchers.HasLength(self.NUM_INSTANCES - 3))
        self.assertThat(self.processor.entity_graph.get_vertices(),
                        matchers.HasLength(
                            self._num_total_expected_vertices() - 3)
                        )
        self.assertThat(deleted_instance_vertices, matchers.HasLength(3))

    def _periodic_process_setup_stage(self, consistency_interval):
        self._create_processor_with_graph(self.conf, processor=self.processor)
        current_time = utcnow()

        # set all vertices to be have timestamp that consistency won't get
        self._update_timestamp(self.processor.entity_graph.get_vertices(),
                               current_time +
                               timedelta(seconds=1.5 * consistency_interval))

        # check number of instances in graph
        instance_vertices = self.processor.entity_graph.get_vertices({
            VProps.VITRAGE_CATEGORY: EntityCategory.RESOURCE,
            VProps.VITRAGE_TYPE: NOVA_INSTANCE_DATASOURCE
        })
        self.assertThat(instance_vertices,
                        matchers.HasLength(self.NUM_INSTANCES))

        # set current timestamp of part of the instances
        self._update_timestamp(instance_vertices[0:3], current_time)

        # set part of the instances as deleted
        for i in range(3, 6):
            instance_vertices[i][VProps.VITRAGE_IS_DELETED] = True
            self.processor.entity_graph.update_vertex(instance_vertices[i])

        # set part of the instances as deleted
        for i in range(6, 9):
            instance_vertices[i][VProps.VITRAGE_IS_DELETED] = True
            instance_vertices[i][VProps.VITRAGE_SAMPLE_TIMESTAMP] = str(
                current_time + timedelta(seconds=2 * consistency_interval + 1))
            self.processor.entity_graph.update_vertex(instance_vertices[i])

    def _set_end_messages(self):
        self.initialization_status.end_messages[NOVA_ZONE_DATASOURCE] = True
        self.initialization_status.end_messages[NOVA_HOST_DATASOURCE] = True
        self.initialization_status.end_messages[NOVA_INSTANCE_DATASOURCE] = \
            True
        self.initialization_status.end_messages[NAGIOS_DATASOURCE] = True

    def _add_alarms(self):
        # find hosts and instances
        host_vertices = self.processor.entity_graph.get_vertices({
            VProps.VITRAGE_CATEGORY: EntityCategory.RESOURCE,
            VProps.VITRAGE_TYPE: NOVA_HOST_DATASOURCE
        })

        # add host alarms + deduced alarms
        self.evaluator.enabled = True
        alarms_on_hosts_list = []
        for index, host_vertex in enumerate(host_vertices):
            alarm_name = '%s:%s' % ('nagios_alarm_on_host_',
                                    host_vertex[VProps.NAME])
            alarms_on_hosts_list.append(
                self._create_alarm(alarm_name, NAGIOS_DATASOURCE))
            self.processor.entity_graph.add_vertex(alarms_on_hosts_list[index])
            edge = graph_utils.create_edge(
                alarms_on_hosts_list[index].vertex_id,
                host_vertex.vertex_id,
                EdgeLabel.ON)
            self.processor.entity_graph.add_edge(edge)

            # reliable action to check that the events in the queue
            while self.event_queue.empty():
                time.sleep(0.1)

            while not self.event_queue.empty():
                self.processor.process_event(self.event_queue.get())

        # remove external alarms
        self.evaluator.enabled = False
        self.processor.entity_graph.remove_vertex(alarms_on_hosts_list[2])
        self.processor.entity_graph.remove_vertex(alarms_on_hosts_list[3])
        self.evaluator.enabled = True

    def _update_timestamp(self, lst, timestamp):
        for vertex in lst:
            vertex[VProps.VITRAGE_SAMPLE_TIMESTAMP] = str(timestamp)
            self.processor.entity_graph.update_vertex(vertex)

    def _process_events(self):
        num_retries = 0
        while True:
            if self.event_queue.empty():
                time.sleep(0.3)

            if not self.event_queue.empty():
                time.sleep(1)
                count = 0
                while not self.event_queue.empty():
                    count += 1
                    event = self.event_queue.get()
                    self.processor.process_event(event)
                return

            num_retries += 1
            if num_retries == 30:
                return
