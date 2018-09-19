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

from debtcollector import removals
from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.common.constants import EntityCategory
from vitrage.common.constants import GraphAction
from vitrage.common.constants import VertexProperties as VProps
from vitrage.datasources.nova.host import NOVA_HOST_DATASOURCE
from vitrage.datasources.resource_transformer_base import \
    ResourceTransformerBase
from vitrage.datasources.static import StaticFields
from vitrage.datasources.static_physical import STATIC_PHYSICAL_DATASOURCE
from vitrage.datasources.static_physical import SWITCH
from vitrage.datasources import transformer_base
import vitrage.graph.utils as graph_utils


class StaticPhysicalTransformer(ResourceTransformerBase):

    RELATION_TYPE = 'relation_type'
    RELATIONSHIPS_SECTION = 'relationships'

    # graph actions which need to refer them differently
    GRAPH_ACTION_MAPPING = {
        GraphAction.DELETE_ENTITY: GraphAction.DELETE_ENTITY
    }

    def __init__(self, transformers, conf):
        removals.removed_module(__name__, "datasources.static")
        super(StaticPhysicalTransformer, self).__init__(transformers, conf)
        self._register_relations_direction()

    def _create_snapshot_entity_vertex(self, entity_event):
        return self._create_vertex(entity_event)

    def _create_update_entity_vertex(self, entity_event):
        return self._create_vertex(entity_event)

    def _create_vertex(self, entity_event):

        entity_type = entity_event[StaticFields.TYPE]
        entity_id = entity_event[VProps.ID]
        vitrage_sample_timestamp = entity_event[DSProps.SAMPLE_DATE]
        update_timestamp = self._format_update_timestamp(
            update_timestamp=None,
            sample_timestamp=vitrage_sample_timestamp)
        state = entity_event[VProps.STATE]
        entity_key = self._create_entity_key(entity_event)
        metadata = self._extract_metadata(entity_event)

        return graph_utils.create_vertex(
            entity_key,
            vitrage_category=EntityCategory.RESOURCE,
            vitrage_type=entity_type,
            vitrage_sample_timestamp=vitrage_sample_timestamp,
            entity_id=entity_id,
            update_timestamp=update_timestamp,
            entity_state=state,
            metadata=metadata)

    def _create_snapshot_neighbors(self, entity_event):
        return self._create_static_physical_neighbors(entity_event)

    def _create_update_neighbors(self, entity_event):
        return self._create_static_physical_neighbors(entity_event)

    def _create_static_physical_neighbors(self, entity_event):
        neighbors = []
        entity_type = entity_event[StaticFields.TYPE]

        for neighbor_details in entity_event.get(
                self.RELATIONSHIPS_SECTION, {}):
            # TODO(alexey): need to decide what to do if one of the entities
            #               fails
            neighbor_id = neighbor_details[VProps.ID]
            neighbor_type = neighbor_details[StaticFields.TYPE]
            relation_type = neighbor_details[self.RELATION_TYPE]
            is_entity_source = not self._find_relation_direction_source(
                entity_type, neighbor_type)
            neighbor = self._create_neighbor(entity_event,
                                             neighbor_id,
                                             neighbor_type,
                                             relation_type,
                                             is_entity_source=is_entity_source)
            if neighbor is not None:
                neighbors.append(neighbor)

        return neighbors

    def _create_entity_key(self, entity_event):
        entity_id = entity_event[VProps.ID]
        entity_type = entity_event[StaticFields.TYPE]
        key_fields = self._key_values(entity_type, entity_id)
        return transformer_base.build_key(key_fields)

    @staticmethod
    def _extract_metadata(entity_event):
        metadata = {VProps.NAME: entity_event[VProps.NAME]}
        return metadata

    def _find_relation_direction_source(self, entity_type, neighbor_type):
        # TODO(alexey): maybe check if this type exists, because it throws
        #               exception if it doesn't
        return self.relation_direction[(entity_type, neighbor_type)]

    def _register_relations_direction(self):
        self.relation_direction = {}

        relationship = (SWITCH, NOVA_HOST_DATASOURCE)
        self.relation_direction[relationship] = True

        relationship = (SWITCH, SWITCH)
        self.relation_direction[relationship] = True

    def get_vitrage_type(self):
        return STATIC_PHYSICAL_DATASOURCE
