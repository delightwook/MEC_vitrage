# Copyright 2016 - Alcatel-Lucent
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
from testtools import matchers

from vitrage.common.constants import DatasourceAction
from vitrage.common.constants import DatasourceOpts as DSOpts
from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.common.constants import EdgeLabel
from vitrage.common.constants import EntityCategory
from vitrage.common.constants import GraphAction
from vitrage.common.constants import UpdateMethod
from vitrage.common.constants import VertexProperties as VProps
from vitrage.datasources.nova.host import NOVA_HOST_DATASOURCE
from vitrage.datasources.nova.host.transformer import HostTransformer
from vitrage.datasources.nova.instance import NOVA_INSTANCE_DATASOURCE
from vitrage.datasources.nova.instance.transformer import InstanceTransformer
from vitrage.datasources import transformer_base as tbase
from vitrage.datasources.transformer_base import TransformerBase
from vitrage.tests import base
from vitrage.tests.mocks import mock_driver as mock_sync

LOG = logging.getLogger(__name__)


# noinspection PyProtectedMember
class NovaInstanceTransformerTest(base.BaseTest):

    OPTS = [
        cfg.StrOpt(DSOpts.UPDATE_METHOD,
                   default=UpdateMethod.PUSH),
    ]

    # noinspection PyAttributeOutsideInit,PyPep8Naming
    @classmethod
    def setUpClass(cls):
        super(NovaInstanceTransformerTest, cls).setUpClass()
        cls.transformers = {}
        cls.conf = cfg.ConfigOpts()
        cls.conf.register_opts(cls.OPTS, group=NOVA_INSTANCE_DATASOURCE)
        cls.transformers[NOVA_HOST_DATASOURCE] = HostTransformer(
            cls.transformers, cls.conf)
        cls.transformers[NOVA_INSTANCE_DATASOURCE] = \
            InstanceTransformer(cls.transformers, cls.conf)

    def test_create_placeholder_vertex(self):
        LOG.debug('Test create placeholder vertex')

        # Tests setup
        instance_id = 'Instance123'
        timestamp = datetime.datetime.utcnow()
        properties = {
            VProps.ID: instance_id,
            VProps.VITRAGE_TYPE: NOVA_INSTANCE_DATASOURCE,
            VProps.VITRAGE_CATEGORY: EntityCategory.RESOURCE,
            VProps.VITRAGE_SAMPLE_TIMESTAMP: timestamp
        }
        transformer = self.transformers[NOVA_INSTANCE_DATASOURCE]

        # Test action
        placeholder = \
            transformer.create_neighbor_placeholder_vertex(**properties)

        # Test assertions
        observed_uuid = placeholder.vertex_id
        expected_key = tbase.build_key(transformer._key_values(
            NOVA_INSTANCE_DATASOURCE,
            instance_id))
        expected_uuid = \
            TransformerBase.uuid_from_deprecated_vitrage_id(expected_key)
        self.assertEqual(expected_uuid, observed_uuid)

        observed_time = placeholder.get(VProps.VITRAGE_SAMPLE_TIMESTAMP)
        self.assertEqual(timestamp, observed_time)

        observed_type = placeholder.get(VProps.VITRAGE_TYPE)
        self.assertEqual(NOVA_INSTANCE_DATASOURCE, observed_type)

        observed_entity_id = placeholder.get(VProps.ID)
        self.assertEqual(instance_id, observed_entity_id)

        observed_vitrage_category = placeholder.get(VProps.VITRAGE_CATEGORY)
        self.assertEqual(EntityCategory.RESOURCE, observed_vitrage_category)

        vitrage_is_placeholder = placeholder.get(VProps.VITRAGE_IS_PLACEHOLDER)
        self.assertTrue(vitrage_is_placeholder)

    def test_snapshot_event_transform(self):
        LOG.debug('Test tactual transform action for '
                  'snapshot and snapshot init events')

        # Test setup
        spec_list = mock_sync.simple_instance_generators(host_num=1,
                                                         vm_num=1,
                                                         snapshot_events=10,
                                                         update_events=0)
        instance_events = mock_sync.generate_random_events_list(spec_list)

        for event in instance_events:
            # Test action
            wrapper = self.transformers[NOVA_INSTANCE_DATASOURCE].transform(
                event)

            # Test assertions
            self._validate_vertex_props(wrapper.vertex, event)

            self.assertThat(wrapper.neighbors, matchers.HasLength(1),
                            'Instance has only one host neighbor')
            host_neighbor = wrapper.neighbors[0]
            self._validate_host_neighbor(host_neighbor, event)

            datasource_action = event[DSProps.DATASOURCE_ACTION]
            if datasource_action == DatasourceAction.INIT_SNAPSHOT:
                self.assertEqual(GraphAction.CREATE_ENTITY, wrapper.action)
            elif datasource_action == DatasourceAction.SNAPSHOT:
                self.assertEqual(GraphAction.UPDATE_ENTITY, wrapper.action)

    def test_update_event_transform(self):
        LOG.debug('Test tactual transform action for update events')

        # Test setup
        spec_list = mock_sync.simple_instance_generators(host_num=1,
                                                         vm_num=1,
                                                         snapshot_events=0,
                                                         update_events=10)
        instance_events = mock_sync.generate_random_events_list(spec_list)

        for event in instance_events:
            # Test action
            wrapper = self.transformers[NOVA_INSTANCE_DATASOURCE].transform(
                event)

            # Test assertions
            self._validate_vertex_props(wrapper.vertex, event)

            # Validate the neighbors: only one  valid host neighbor
            neighbors = wrapper.neighbors
            self.assertThat(neighbors, matchers.HasLength(1))
            self._validate_host_neighbor(neighbors[0], event)

            event_type = event[DSProps.EVENT_TYPE]
            if event_type == 'compute.instance.delete.end':
                self.assertEqual(GraphAction.DELETE_ENTITY, wrapper.action)
            elif event_type == 'compute.instance.create.start':
                self.assertEqual(GraphAction.CREATE_ENTITY, wrapper.action)
            else:
                self.assertEqual(GraphAction.UPDATE_ENTITY, wrapper.action)

    def _validate_vertex_props(self, vertex, event):

        self.assertThat(vertex.properties, matchers.HasLength(13))

        is_update_event = tbase.is_update_event(event)

        extract_value = tbase.extract_field_value

        instance_id = 'instance_id' if is_update_event else 'id'
        expected_id = extract_value(event, instance_id)
        observed_id = vertex[VProps.ID]
        self.assertEqual(expected_id, observed_id)

        self.assertEqual(
            EntityCategory.RESOURCE,
            vertex[VProps.VITRAGE_CATEGORY]
        )
        self.assertEqual(NOVA_INSTANCE_DATASOURCE,
                         vertex[VProps.VITRAGE_TYPE])

        expected_project = extract_value(event, 'tenant_id')
        observed_project = vertex[VProps.PROJECT_ID]
        self.assertEqual(expected_project, observed_project)

        state = 'state' if is_update_event else 'status'
        expected_state = extract_value(event, state)
        observed_state = vertex[VProps.STATE]
        self.assertEqual(expected_state, observed_state)

        expected_timestamp = event[DSProps.SAMPLE_DATE]
        observed_timestamp = vertex[VProps.VITRAGE_SAMPLE_TIMESTAMP]
        self.assertEqual(expected_timestamp, observed_timestamp)

        name = 'hostname' if is_update_event else 'name'
        expected_name = extract_value(event, name)
        observed_name = vertex[VProps.NAME]
        self.assertEqual(expected_name, observed_name)

        vitrage_is_placeholder = vertex[VProps.VITRAGE_IS_PLACEHOLDER]
        self.assertFalse(vitrage_is_placeholder)

        vitrage_is_deleted = vertex[VProps.VITRAGE_IS_DELETED]
        self.assertFalse(vitrage_is_deleted)

    def _validate_host_neighbor(self, h_neighbor, event):

        it = self.transformers[NOVA_INSTANCE_DATASOURCE]

        name = 'host' if tbase.is_update_event(event) \
            else 'OS-EXT-SRV-ATTR:host'
        host_name = tbase.extract_field_value(event, name)
        time = event[DSProps.SAMPLE_DATE]

        ht = self.transformers[NOVA_HOST_DATASOURCE]
        properties = {
            VProps.ID: host_name,
            VProps.VITRAGE_TYPE: NOVA_HOST_DATASOURCE,
            VProps.VITRAGE_CATEGORY: EntityCategory.RESOURCE,
            VProps.VITRAGE_SAMPLE_TIMESTAMP: time
        }
        expected_neighbor = \
            ht.create_neighbor_placeholder_vertex(**properties)
        self.assertEqual(expected_neighbor, h_neighbor.vertex)

        # Validate neighbor edge
        edge = h_neighbor.edge
        entity_key = it._create_entity_key(event)
        entity_uuid = \
            TransformerBase.uuid_from_deprecated_vitrage_id(entity_key)
        self.assertEqual(edge.source_id, h_neighbor.vertex.vertex_id)
        self.assertEqual(edge.target_id, entity_uuid)
        self.assertEqual(edge.label, EdgeLabel.CONTAINS)

    def test_create_entity_key(self):
        LOG.debug('Test get key from nova instance transformer')

        # Test setup
        spec_list = mock_sync.simple_instance_generators(
            host_num=1,
            vm_num=1,
            snapshot_events=1,
            update_events=0
        )
        instance_events = mock_sync.generate_random_events_list(spec_list)

        instance_transformer = self.transformers[NOVA_INSTANCE_DATASOURCE]
        for event in instance_events:
            # Test action
            observed_key = instance_transformer._create_entity_key(event)

            # Test assertions
            observed_key_fields = observed_key.split(
                TransformerBase.KEY_SEPARATOR)

            self.assertEqual(EntityCategory.RESOURCE, observed_key_fields[0])
            self.assertEqual(
                NOVA_INSTANCE_DATASOURCE,
                observed_key_fields[1]
            )

            instance_id = tbase.extract_field_value(event, 'id')

            self.assertEqual(instance_id, observed_key_fields[2])

            key_values = instance_transformer._key_values(
                NOVA_INSTANCE_DATASOURCE,
                instance_id)
            expected_key = tbase.build_key(key_values)

            self.assertEqual(expected_key, observed_key)

    def test_build_instance_key(self):
        LOG.debug('Test build instance key')

        # Test setup
        instance_id = '456'
        expected_key = 'RESOURCE:nova.instance:%s' % instance_id

        instance_transformer = self.transformers[NOVA_INSTANCE_DATASOURCE]
        # Test action
        key_fields = instance_transformer._key_values(
            NOVA_INSTANCE_DATASOURCE,
            instance_id)

        # Test assertions
        observed_key = tbase.build_key(key_fields)
        self.assertEqual(expected_key, observed_key)

    def test_create_host_neighbor(self):
        LOG.debug('Test create host neighbor')

        # Test setup
        host_name = 'host123'
        vertex_key = 'RESOURCE:nova.instance:instance321'
        vertex_id = \
            TransformerBase.uuid_from_deprecated_vitrage_id(vertex_key)
        time = datetime.datetime.utcnow()
        entity_event = {
            '_info': {
                'host_name': host_name
            },
            DSProps.DATASOURCE_ACTION: 'SNAPSHOT',
            'id': 'instance321',
            DSProps.SAMPLE_DATE: time
        }

        # Test action
        instance_transformer = self.transformers[NOVA_INSTANCE_DATASOURCE]
        neighbor = \
            instance_transformer._create_neighbor(entity_event,
                                                  host_name,
                                                  NOVA_HOST_DATASOURCE,
                                                  EdgeLabel.CONTAINS,
                                                  is_entity_source=False)

        # Test assertions
        host_vertex_id = \
            TransformerBase.uuid_from_deprecated_vitrage_id(
                'RESOURCE:nova.host:host123')
        self.assertEqual(host_vertex_id, neighbor.vertex.vertex_id)
        self.assertEqual(
            time,
            neighbor.vertex.get(VProps.VITRAGE_SAMPLE_TIMESTAMP)
        )

        # test relation edge
        self.assertEqual(host_vertex_id, neighbor.edge.source_id)
        self.assertEqual(vertex_id, neighbor.edge.target_id)
        self.assertEqual(EdgeLabel.CONTAINS, neighbor.edge.label)
