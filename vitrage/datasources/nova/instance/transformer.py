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
from oslo_log import log as logging

from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.common.constants import EdgeLabel
from vitrage.common.constants import EntityCategory
from vitrage.common.constants import GraphAction
from vitrage.common.constants import VertexProperties as VProps
from vitrage.datasources.nova.host import NOVA_HOST_DATASOURCE
from vitrage.datasources.nova.instance import NOVA_INSTANCE_DATASOURCE
from vitrage.datasources.resource_transformer_base import \
    ResourceTransformerBase
from vitrage.datasources import transformer_base as tbase
from vitrage.datasources.transformer_base import extract_field_value
import vitrage.graph.utils as graph_utils

LOG = logging.getLogger(__name__)


class InstanceTransformer(ResourceTransformerBase):

    # graph actions which need to refer them differently
    GRAPH_ACTION_MAPPING = {
        'compute.instance.delete.end': GraphAction.DELETE_ENTITY,
    }

    def __init__(self, transformers, conf):
        super(InstanceTransformer, self).__init__(transformers, conf)

    def _create_snapshot_entity_vertex(self, entity_event):

        name = extract_field_value(entity_event, 'name')
        entity_id = extract_field_value(entity_event, 'id')
        state = extract_field_value(entity_event, 'status')
        host = extract_field_value(entity_event, 'OS-EXT-SRV-ATTR:host')

        return self._create_vertex(entity_event, name, entity_id, state, host)

    def _create_update_entity_vertex(self, entity_event):

        name = extract_field_value(entity_event, 'hostname')
        entity_id = extract_field_value(entity_event, 'instance_id')
        state = extract_field_value(entity_event, 'state')
        host = extract_field_value(entity_event, 'host')

        return self._create_vertex(entity_event, name, entity_id, state, host)

    def _create_vertex(self, entity_event, name, entity_id, state, host):

        metadata = {
            VProps.NAME: name,
            VProps.PROJECT_ID: entity_event.get('tenant_id', None),
            'host_id': host
        }

        vitrage_sample_timestamp = entity_event[DSProps.SAMPLE_DATE]

        # TODO(Alexey): need to check that only the UPDATE datasource_action
        # will update the UPDATE_TIMESTAMP property
        update_timestamp = self._format_update_timestamp(
            extract_field_value(entity_event, DSProps.SAMPLE_DATE),
            vitrage_sample_timestamp)

        return graph_utils.create_vertex(
            self._create_entity_key(entity_event),
            vitrage_category=EntityCategory.RESOURCE,
            vitrage_type=NOVA_INSTANCE_DATASOURCE,
            vitrage_sample_timestamp=vitrage_sample_timestamp,
            entity_id=entity_id,
            entity_state=state,
            update_timestamp=update_timestamp,
            metadata=metadata)

    def _create_snapshot_neighbors(self, entity_event):
        return self._create_instance_neighbors(entity_event,
                                               'OS-EXT-SRV-ATTR:host')

    def _create_update_neighbors(self, entity_event):
        return self._create_instance_neighbors(entity_event,
                                               'host')

    def _create_instance_neighbors(self, entity_event, host_property_name):
        host_name = entity_event.get(host_property_name)
        host_neighbor = self._create_neighbor(entity_event,
                                              host_name,
                                              NOVA_HOST_DATASOURCE,
                                              EdgeLabel.CONTAINS,
                                              is_entity_source=False)

        return [host_neighbor]

    def _create_entity_key(self, event):
        LOG.debug('Creating key for instance event: %s', str(event))

        instance_id = 'instance_id' if tbase.is_update_event(event) else 'id'
        key_fields = self._key_values(NOVA_INSTANCE_DATASOURCE,
                                      extract_field_value(event,
                                                          instance_id))
        key = tbase.build_key(key_fields)
        LOG.debug('Created key: %s', key)

        return key

    def get_vitrage_type(self):
        return NOVA_INSTANCE_DATASOURCE
