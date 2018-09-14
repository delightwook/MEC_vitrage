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

from oslo_log import log

from vitrage.common.constants import DatasourceAction
from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.common.constants import EntityCategory
from vitrage.common.constants import GraphAction
from vitrage.common.constants import VertexProperties as VProps
from vitrage.datasources.consistency import CONSISTENCY_DATASOURCE
from vitrage.datasources import OPENSTACK_CLUSTER
from vitrage.entity_graph import EVALUATOR_TOPIC
from vitrage.evaluator.actions.evaluator_event_transformer \
    import VITRAGE_DATASOURCE
from vitrage.messaging import VitrageNotifier
from vitrage.utils.datetime import utcnow

LOG = log.getLogger(__name__)


class ConsistencyEnforcer(object):

    def __init__(self,
                 conf,
                 entity_graph,
                 actions_callback=None):
        self.conf = conf
        self.actions_callback = actions_callback or VitrageNotifier(
            conf, 'vitrage_consistency', [EVALUATOR_TOPIC]).notify
        self.graph = entity_graph

    def periodic_process(self):
        try:
            LOG.info('Periodic consistency check..')

            old_deleted_entities = self._find_old_deleted_entities()
            LOG.debug('Found %s vertices to be deleted by consistency service'
                      ': %s', len(old_deleted_entities), old_deleted_entities)
            self._push_events_to_queue(old_deleted_entities,
                                       GraphAction.REMOVE_DELETED_ENTITY)

            stale_entities = self._find_placeholder_entities()
            LOG.debug('Found %s vertices to be marked as deleted by '
                      'consistency service: %s', len(stale_entities),
                      stale_entities)
            self._push_events_to_queue(stale_entities,
                                       GraphAction.DELETE_ENTITY)
        except Exception:
            LOG.exception('Error in deleting vertices from entity_graph.')

    def _find_placeholder_entities(self):
        vitrage_sample_tstmp = str(utcnow() - timedelta(
            seconds=2 * self.conf.datasources.snapshots_interval))
        query = {
            'and': [
                {'!=': {VProps.VITRAGE_TYPE: VITRAGE_DATASOURCE}},
                {'<': {VProps.VITRAGE_SAMPLE_TIMESTAMP: vitrage_sample_tstmp}},
                {'==': {VProps.VITRAGE_IS_DELETED: False}},
                {'==': {VProps.VITRAGE_IS_PLACEHOLDER: True}},
            ]
        }

        vertices = self.graph.get_vertices(query_dict=query)

        return set(self._filter_vertices_to_be_deleted(vertices))

    def _find_old_deleted_entities(self):
        vitrage_sample_tstmp = str(utcnow() - timedelta(
            seconds=self.conf.consistency.min_time_to_delete))
        query = {
            'and': [
                {'==': {VProps.VITRAGE_IS_DELETED: True}},
                {'<': {VProps.VITRAGE_SAMPLE_TIMESTAMP: vitrage_sample_tstmp}}
            ]
        }

        vertices = self.graph.get_vertices(query_dict=query)

        return self._filter_vertices_to_be_deleted(vertices)

    def _push_events_to_queue(self, vertices, action):
        for vertex in vertices:
            event = {
                DSProps.ENTITY_TYPE: CONSISTENCY_DATASOURCE,
                DSProps.DATASOURCE_ACTION: DatasourceAction.UPDATE,
                DSProps.SAMPLE_DATE: str(utcnow()),
                DSProps.EVENT_TYPE: action,
                VProps.VITRAGE_ID: vertex[VProps.VITRAGE_ID],
                VProps.ID: vertex.get(VProps.ID, None),
                VProps.VITRAGE_TYPE: vertex[VProps.VITRAGE_TYPE],
                VProps.VITRAGE_CATEGORY: vertex[VProps.VITRAGE_CATEGORY],
                VProps.IS_REAL_VITRAGE_ID: True
            }
            self.actions_callback('consistency', event)

    @staticmethod
    def _filter_vertices_to_be_deleted(vertices):
        return list(filter(
            lambda ver:
            not (ver[VProps.VITRAGE_CATEGORY] == EntityCategory.RESOURCE and
                 ver[VProps.VITRAGE_TYPE] == OPENSTACK_CLUSTER), vertices))

    def _wait_for_action(self, function):
        count_retries = 0
        while True:
            if count_retries >= \
                    self.conf.consistency.initialization_max_retries:
                return False

            if function():
                return True

            count_retries += 1
            time.sleep(self.conf.consistency.initialization_interval)
