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

from vitrage.datasources.resource_transformer_base import \
    ResourceTransformerBase

from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.common.constants import EdgeLabel
from vitrage.common.constants import EntityCategory
from vitrage.common.constants import GraphAction
from vitrage.common.constants import VertexProperties as VProps
from vitrage.datasources.neutron.network import NEUTRON_NETWORK_DATASOURCE
from vitrage.datasources.neutron.port import NEUTRON_PORT_DATASOURCE
from vitrage.datasources.nova.instance import NOVA_INSTANCE_DATASOURCE
from vitrage.datasources import transformer_base as tbase
from vitrage.datasources.transformer_base import extract_field_value

import vitrage.graph.utils as graph_utils


class PortTransformer(ResourceTransformerBase):

    UPDATE_ID_PROPERTY = {
        'port.create.end': ('port', 'id'),
        'port.update.end': ('port', 'id'),
        'port.delete.end': ('port_id',),
        None: ('id',)
    }

    FIXED_IPS_PROPERTY = {
        'port.create.end': ('port', 'fixed_ips'),
        'port.update.end': ('port', 'fixed_ips'),
        None: ('fixed_ips',)
    }

    # graph actions which need to refer them differently
    GRAPH_ACTION_MAPPING = {
        'port.delete.end': GraphAction.DELETE_ENTITY,
    }

    def __init__(self, transformers, conf):
        super(PortTransformer, self).__init__(transformers, conf)

    def _create_snapshot_entity_vertex(self, entity_event):

        name = entity_event['name'] if entity_event['name'] else None
        entity_id = entity_event['id']
        state = entity_event['status']
        update_timestamp = entity_event['updated_at']
        project_id = entity_event.get('tenant_id', None)

        return self._create_vertex(entity_event,
                                   name,
                                   entity_id,
                                   state,
                                   update_timestamp,
                                   project_id)

    def _create_update_entity_vertex(self, entity_event):

        event_type = entity_event[DSProps.EVENT_TYPE]
        name = extract_field_value(entity_event, 'port', 'name')
        state = extract_field_value(entity_event, 'port', 'status')
        update_timestamp = \
            extract_field_value(entity_event, 'port', 'updated_at')
        entity_id = extract_field_value(entity_event,
                                        *self.UPDATE_ID_PROPERTY[event_type])
        project_id = extract_field_value(entity_event, 'port', 'tenant_id')

        return self._create_vertex(entity_event,
                                   name,
                                   entity_id,
                                   state,
                                   update_timestamp,
                                   project_id)

    def _create_vertex(self,
                       entity_event,
                       name,
                       entity_id,
                       state,
                       update_timestamp,
                       project_id):
        event_type = entity_event.get(DSProps.EVENT_TYPE, None)
        ip_addresses = []
        if not event_type:
            fixed_ips = extract_field_value(
                entity_event, *self.FIXED_IPS_PROPERTY[event_type])
            ip_addresses = [ip['ip_address'] for ip in fixed_ips]
        metadata = {
            VProps.NAME: name,
            VProps.PROJECT_ID: project_id,
            'ip_addresses': tuple(ip_addresses),
            'host_id': entity_event.get('binding:host_id'),
        }

        vitrage_sample_timestamp = entity_event[DSProps.SAMPLE_DATE]

        return graph_utils.create_vertex(
            self._create_entity_key(entity_event),
            vitrage_category=EntityCategory.RESOURCE,
            vitrage_type=NEUTRON_PORT_DATASOURCE,
            vitrage_sample_timestamp=vitrage_sample_timestamp,
            entity_id=entity_id,
            entity_state=state,
            update_timestamp=update_timestamp,
            metadata=metadata)

    def _create_snapshot_neighbors(self, entity_event):
        return self._create_port_neighbors(entity_event,
                                           ('device_id',),
                                           ('network_id',))

    def _create_update_neighbors(self, entity_event):
        return self._create_port_neighbors(entity_event,
                                           ('port', 'device_id'),
                                           ('port', 'network_id'))

    def _create_port_neighbors(self,
                               entity_event,
                               device_id_property,
                               network_id_property):
        network_neighbor_id = extract_field_value(entity_event,
                                                  *network_id_property)
        neighbors = [self._create_neighbor(entity_event,
                                           network_neighbor_id,
                                           NEUTRON_NETWORK_DATASOURCE,
                                           EdgeLabel.CONTAINS,
                                           is_entity_source=False)]

        instance_neighbor_id = \
            extract_field_value(entity_event, *device_id_property)
        instance = self._create_neighbor(entity_event,
                                         instance_neighbor_id,
                                         NOVA_INSTANCE_DATASOURCE,
                                         EdgeLabel.ATTACHED,
                                         is_entity_source=True)
        neighbors.append(instance)

        return neighbors

    def _create_entity_key(self, entity_event):
        event_type = entity_event.get(DSProps.EVENT_TYPE, None)
        port_id = extract_field_value(entity_event,
                                      *self.UPDATE_ID_PROPERTY[event_type])

        key_fields = self._key_values(NEUTRON_PORT_DATASOURCE, port_id)

        return tbase.build_key(key_fields)

    def get_vitrage_type(self):
        return NEUTRON_PORT_DATASOURCE
