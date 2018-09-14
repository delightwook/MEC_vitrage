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

from vitrage.common.constants import DatasourceAction as DSAction
from vitrage.common.constants import GraphAction
from vitrage.common.constants import VertexProperties as VProps
from vitrage.entity_graph.mappings.operational_resource_state import \
    OperationalResourceState
from vitrage.tests.functional.base import TestFunctionalBase


class TestDatasourceInfoMapperFunctional(TestFunctionalBase):

    # noinspection PyAttributeOutsideInit,PyPep8Naming
    @classmethod
    def setUpClass(cls):
        super(TestDatasourceInfoMapperFunctional, cls).setUpClass()
        cls.conf = cfg.ConfigOpts()
        cls.conf.register_opts(cls.PROCESSOR_OPTS, group='entity_graph')
        cls.conf.register_opts(cls.DATASOURCES_OPTS, group='datasources')
        cls.load_datasources(cls.conf)

    def test_state_on_update(self):
        # setup
        processor = self.create_processor_and_graph(self.conf)
        event = self._create_event(spec_type='INSTANCE_SPEC',
                                   datasource_action=DSAction.INIT_SNAPSHOT)

        # action
        processor.process_event(event)

        # test assertions
        entity = processor.transformer_manager.transform(event)
        vertex = processor.entity_graph.get_vertex(entity.vertex.vertex_id)
        self.assertEqual('ACTIVE', vertex[VProps.VITRAGE_AGGREGATED_STATE])
        self.assertEqual(OperationalResourceState.OK,
                         vertex[VProps.VITRAGE_OPERATIONAL_STATE])

    def test_state_on_neighbor_update(self):
        # setup
        vertex, neighbors, processor = self._create_entity(
            spec_type='INSTANCE_SPEC',
            datasource_action=DSAction.INIT_SNAPSHOT)
        self.assertEqual(2, processor.entity_graph.num_vertices())

        neighbors[0].vertex[VProps.STATE] = 'available'
        neighbors[0].vertex[VProps.VITRAGE_IS_PLACEHOLDER] = False

        # action
        processor._connect_neighbors(neighbors, [], GraphAction.UPDATE_ENTITY)

        # test assertions
        neighbor_vertex = processor.entity_graph.get_vertex(
            neighbors[0].vertex.vertex_id)
        self.assertEqual('AVAILABLE',
                         neighbor_vertex[VProps.VITRAGE_AGGREGATED_STATE])
        self.assertEqual(OperationalResourceState.OK,
                         neighbor_vertex[VProps.VITRAGE_OPERATIONAL_STATE])
