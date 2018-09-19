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

from oslo_config import cfg
from vitrage.datasources.cinder.volume.driver import CINDER_VOLUME_DATASOURCE

from vitrage.common.constants import DatasourceAction
from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.common.constants import EntityCategory
from vitrage.datasources.nagios import NAGIOS_DATASOURCE
from vitrage.datasources.neutron.network import NEUTRON_NETWORK_DATASOURCE
from vitrage.datasources.neutron.port import NEUTRON_PORT_DATASOURCE
from vitrage.datasources.nova.host import NOVA_HOST_DATASOURCE
from vitrage.datasources.nova.instance import NOVA_INSTANCE_DATASOURCE
from vitrage.datasources.nova.zone import NOVA_ZONE_DATASOURCE
from vitrage.entity_graph.processor import processor as proc
from vitrage.graph.driver.networkx_graph import NXGraph
import vitrage.graph.utils as graph_utils
from vitrage.opts import register_opts
from vitrage.tests import base
from vitrage.tests.mocks import mock_driver as mock_sync
from vitrage.tests.mocks import utils


class TestEntityGraphUnitBase(base.BaseTest):

    PROCESSOR_OPTS = [
        cfg.StrOpt('datasources_values_dir',
                   default=utils.get_resources_dir() + '/datasources_values'),
    ]

    DATASOURCES_OPTS = [
        cfg.ListOpt('types',
                    default=[NAGIOS_DATASOURCE,
                             NOVA_HOST_DATASOURCE,
                             NOVA_INSTANCE_DATASOURCE,
                             NOVA_ZONE_DATASOURCE,
                             NEUTRON_NETWORK_DATASOURCE,
                             NEUTRON_PORT_DATASOURCE,
                             CINDER_VOLUME_DATASOURCE],
                    help='Names of supported data sources'),

        cfg.ListOpt('path',
                    default=['vitrage.datasources'],
                    help='base path for data sources'),

        cfg.IntOpt('snapshots_interval',
                   default=1,
                   min=1)
    ]

    NUM_CLUSTERS = 1
    NUM_ZONES = 2
    NUM_HOSTS = 4
    NUM_INSTANCES = 16

    @staticmethod
    def load_datasources(conf):
        for datasource in conf.datasources.types:
            register_opts(conf, datasource, conf.datasources.path)

    def _create_processor_with_graph(self, conf, processor=None):
        events = self._create_mock_events()

        if not processor:
            processor = self.create_processor_and_graph(conf)

        for event in events:
            processor.process_event(event)

        return processor

    def _create_mock_events(self):
        gen_list = mock_sync.simple_zone_generators(
            self.NUM_ZONES,
            self.NUM_HOSTS,
            snapshot_events=self.NUM_ZONES,
            snap_vals={DSProps.DATASOURCE_ACTION:
                       DatasourceAction.INIT_SNAPSHOT})
        gen_list += mock_sync.simple_host_generators(
            self.NUM_ZONES,
            self.NUM_HOSTS,
            self.NUM_HOSTS,
            snap_vals={DSProps.DATASOURCE_ACTION:
                       DatasourceAction.INIT_SNAPSHOT})
        gen_list += mock_sync.simple_instance_generators(
            self.NUM_HOSTS,
            self.NUM_INSTANCES,
            self.NUM_INSTANCES,
            snap_vals={DSProps.DATASOURCE_ACTION:
                       DatasourceAction.INIT_SNAPSHOT})
        return mock_sync.generate_sequential_events_list(gen_list)

    def _create_entity(self,
                       processor=None,
                       spec_type=None,
                       datasource_action=None,
                       event_type=None,
                       properties=None):
        # create instance event with host neighbor
        event = self._create_event(spec_type=spec_type,
                                   datasource_action=datasource_action,
                                   event_type=event_type,
                                   properties=properties)

        # add instance entity with host
        if processor is None:
            processor = self.create_processor_and_graph(self.conf)

        vertex, neighbors, event_type = processor.transformer_manager\
            .transform(event)
        processor.create_entity(vertex, neighbors)

        return vertex, neighbors, processor

    @staticmethod
    def create_processor_and_graph(conf):
        e_graph = NXGraph("Entity Graph")
        return proc.Processor(conf, e_graph=e_graph)

    @staticmethod
    def _create_event(spec_type=None,
                      datasource_action=None,
                      event_type=None,
                      properties=None):
        # generate event
        spec_list = mock_sync.simple_instance_generators(1, 1, 1)
        events_list = mock_sync.generate_random_events_list(
            spec_list)

        # update properties
        if datasource_action is not None:
            events_list[0][DSProps.DATASOURCE_ACTION] = datasource_action

        if event_type is not None:
            events_list[0][DSProps.EVENT_TYPE] = event_type

        if properties is not None:
            for key, value in properties.items():
                events_list[0][key] = value

        return events_list[0]

    @staticmethod
    def _create_alarm(vitrage_id, alarm_type, project_id=None, metadata=None):
        return graph_utils.create_vertex(
            vitrage_id,
            vitrage_category=EntityCategory.ALARM,
            vitrage_type=alarm_type,
            vitrage_sample_timestamp=None,
            vitrage_is_deleted=False,
            vitrage_is_placeholder=False,
            entity_id=vitrage_id,
            entity_state='active',
            project_id=project_id,
            metadata=metadata
        )

    @staticmethod
    def _create_resource(vitrage_id, resource_type, project_id=None):
        return graph_utils.create_vertex(
            vitrage_id,
            vitrage_category=EntityCategory.RESOURCE,
            vitrage_type=resource_type,
            vitrage_sample_timestamp=None,
            vitrage_is_deleted=False,
            vitrage_is_placeholder=False,
            entity_id=vitrage_id,
            entity_state='active',
            project_id=project_id
        )

    def _num_total_expected_vertices(self):
        return self.NUM_CLUSTERS + self.NUM_ZONES + self.NUM_HOSTS + \
            self.NUM_INSTANCES

    def _num_total_expected_edges(self):
        return self.NUM_CLUSTERS + self.NUM_ZONES + self.NUM_HOSTS + \
            self.NUM_INSTANCES - 1
