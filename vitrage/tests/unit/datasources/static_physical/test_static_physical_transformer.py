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

import datetime

from oslo_config import cfg
from oslo_log import log as logging

from vitrage.common.constants import DatasourceOpts as DSOpts
from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.common.constants import EdgeLabel
from vitrage.common.constants import EntityCategory
from vitrage.common.constants import UpdateMethod
from vitrage.common.constants import VertexProperties as VProps
from vitrage.datasources.nova.host import NOVA_HOST_DATASOURCE
from vitrage.datasources.nova.host.transformer import HostTransformer
from vitrage.datasources.static import StaticFields
from vitrage.datasources.static_physical import STATIC_PHYSICAL_DATASOURCE
from vitrage.datasources.static_physical.transformer \
    import StaticPhysicalTransformer
from vitrage.datasources import transformer_base as tbase
from vitrage.datasources.transformer_base import TransformerBase
from vitrage.tests import base
from vitrage.tests.mocks import mock_driver as mock_sync

LOG = logging.getLogger(__name__)


class TestStaticPhysicalTransformer(base.BaseTest):

    OPTS = [
        cfg.StrOpt(DSOpts.UPDATE_METHOD,
                   default=UpdateMethod.PULL),
    ]

    # noinspection PyAttributeOutsideInit,PyPep8Naming
    @classmethod
    def setUpClass(cls):
        super(TestStaticPhysicalTransformer, cls).setUpClass()
        cls.transformers = {}
        cls.conf = cfg.ConfigOpts()
        cls.conf.register_opts(cls.OPTS, group=STATIC_PHYSICAL_DATASOURCE)
        cls.transformers[NOVA_HOST_DATASOURCE] = HostTransformer(
            cls.transformers, cls.conf)
        cls.transformers[STATIC_PHYSICAL_DATASOURCE] = \
            StaticPhysicalTransformer(cls.transformers, cls.conf)

    def test_create_placeholder_vertex(self):

        LOG.debug('Static Physical transformer test: Create placeholder '
                  'vertex')

        # Test setup
        switch_type = STATIC_PHYSICAL_DATASOURCE
        switch_name = 'switch-1'
        timestamp = datetime.datetime.utcnow()
        static_transformer = self.transformers[STATIC_PHYSICAL_DATASOURCE]

        # Test action
        properties = {
            VProps.VITRAGE_TYPE: switch_type,
            VProps.ID: switch_name,
            VProps.VITRAGE_CATEGORY: EntityCategory.RESOURCE,
            VProps.VITRAGE_SAMPLE_TIMESTAMP: timestamp
        }
        placeholder = \
            static_transformer.create_neighbor_placeholder_vertex(**properties)

        # Test assertions
        observed_uuid = placeholder.vertex_id
        expected_key = tbase.build_key(static_transformer._key_values(
            switch_type, switch_name))
        expected_uuid = \
            TransformerBase.uuid_from_deprecated_vitrage_id(expected_key)
        self.assertEqual(expected_uuid, observed_uuid)

        observed_time = placeholder.get(VProps.VITRAGE_SAMPLE_TIMESTAMP)
        self.assertEqual(timestamp, observed_time)

        observed_subtype = placeholder.get(VProps.VITRAGE_TYPE)
        self.assertEqual(switch_type, observed_subtype)

        observed_entity_id = placeholder.get(VProps.ID)
        self.assertEqual(switch_name, observed_entity_id)

        observed_vitrage_category = placeholder.get(VProps.VITRAGE_CATEGORY)
        self.assertEqual(EntityCategory.RESOURCE, observed_vitrage_category)

        vitrage_is_placeholder = placeholder.get(VProps.VITRAGE_IS_PLACEHOLDER)
        self.assertTrue(vitrage_is_placeholder)

    def test_key_values(self):
        LOG.debug('Static Physical transformer test: get key values')

        # Test setup
        switch_type = STATIC_PHYSICAL_DATASOURCE
        switch_name = 'switch-1'
        static_transformer = self.transformers[STATIC_PHYSICAL_DATASOURCE]

        # Test action
        observed_key_fields = static_transformer._key_values(switch_type,
                                                             switch_name)

        # Test assertions
        self.assertEqual(EntityCategory.RESOURCE, observed_key_fields[0])
        self.assertEqual(STATIC_PHYSICAL_DATASOURCE, observed_key_fields[1])
        self.assertEqual(switch_name, observed_key_fields[2])

    def test_snapshot_transform(self):
        LOG.debug('Test transform entity snapshot/snapshot_init event')

        # Test setup
        spec_list = mock_sync.simple_switch_generators(2, 10, 10)
        static_events = mock_sync.generate_random_events_list(spec_list)
        self._events_transform_test(static_events)

    def test_update_transform(self):
        LOG.debug('Test transform entity update event')

        # Test setup
        spec_list = mock_sync.simple_switch_generators(2, 10, 0, None, 10)
        static_events = mock_sync.generate_random_events_list(spec_list)
        self._events_transform_test(static_events)

    def _events_transform_test(self, events):

        for event in events:
            # Test action
            wrapper = self.transformers[STATIC_PHYSICAL_DATASOURCE].\
                transform(event)

            # Test assertions
            vertex = wrapper.vertex
            self._validate_switch_vertex_props(vertex, event)

            neighbors = wrapper.neighbors
            self._validate_neighbors(neighbors, vertex.vertex_id, event)

    def _validate_neighbors(self, neighbors, switch_vertex_id, event):
        host_counter = 0

        for neighbor in neighbors:
            self._validate_host_neighbor(neighbor,
                                         event['relationships'][host_counter],
                                         switch_vertex_id)
            host_counter += 1

        self.assertEqual(5,
                         host_counter,
                         'Zone can belongs to only one Cluster')

    def _validate_host_neighbor(self,
                                host_neighbor,
                                host_event,
                                switch_vertex_id):
        # validate neighbor vertex
        self._validate_host_vertex_props(host_neighbor.vertex, host_event)

        # Validate neighbor edge
        edge = host_neighbor.edge
        self.assertEqual(edge.target_id, switch_vertex_id)
        self.assertEqual(edge.source_id, host_neighbor.vertex.vertex_id)
        self.assertEqual(edge.label, EdgeLabel.CONTAINS)

    def _validate_common_vertex_props(self, vertex, event):
        self.assertEqual(EntityCategory.RESOURCE,
                         vertex[VProps.VITRAGE_CATEGORY])
        self.assertEqual(event[StaticFields.TYPE],
                         vertex[VProps.VITRAGE_TYPE])
        self.assertEqual(event[StaticFields.ID], vertex[VProps.ID])

    def _validate_switch_vertex_props(self, vertex, event):
        self._validate_common_vertex_props(vertex, event)
        self.assertEqual(event[DSProps.SAMPLE_DATE],
                         vertex[VProps.VITRAGE_SAMPLE_TIMESTAMP])
        self.assertEqual(event[VProps.NAME], vertex[VProps.NAME])
        self.assertEqual(event[VProps.STATE], vertex[VProps.STATE])
        self.assertFalse(vertex[VProps.VITRAGE_IS_PLACEHOLDER])
        self.assertFalse(vertex[VProps.VITRAGE_IS_DELETED])

    def _validate_host_vertex_props(self, vertex, event):
        self._validate_common_vertex_props(vertex, event)
        self.assertTrue(vertex[VProps.VITRAGE_IS_PLACEHOLDER])
        self.assertFalse(vertex[VProps.VITRAGE_IS_DELETED])
