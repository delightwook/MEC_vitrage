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

from oslo_log import log
from osprofiler import profiler


from vitrage.api_handler.apis.base import ALARMS_ALL_QUERY
from vitrage.api_handler.apis.base import EDGE_QUERY
from vitrage.api_handler.apis.base import EntityGraphApisBase
from vitrage.api_handler.apis.base import RCA_QUERY
from vitrage.common.constants import TenantProps
from vitrage.graph import Direction


LOG = log.getLogger(__name__)


@profiler.trace_cls("rca apis",
                    info={}, hide_args=False, trace_private=False)
class RcaApis(EntityGraphApisBase):

    def __init__(self, entity_graph, conf):
        self.entity_graph = entity_graph
        self.conf = conf

    def get_rca(self, ctx, root, all_tenants):
        LOG.debug("RcaApis get_rca - root: %s, all_tenants=%s",
                  str(root), all_tenants)

        project_id = ctx.get(TenantProps.TENANT, None)
        is_admin_project = ctx.get(TenantProps.IS_ADMIN, False)
        ga = self.entity_graph.algo

        found_graph_out = ga.graph_query_vertices(root,
                                                  query_dict=RCA_QUERY,
                                                  direction=Direction.OUT,
                                                  edge_query_dict=EDGE_QUERY)
        found_graph_in = ga.graph_query_vertices(root,
                                                 query_dict=RCA_QUERY,
                                                 direction=Direction.IN,
                                                 edge_query_dict=EDGE_QUERY)

        if all_tenants:
            unified_graph = found_graph_in
            unified_graph.union(found_graph_out)
        else:
            unified_graph = \
                self._get_rca_for_specific_project(ga,
                                                   found_graph_in,
                                                   found_graph_out,
                                                   root,
                                                   project_id,
                                                   is_admin_project)

        alarms = unified_graph.get_vertices(query_dict=ALARMS_ALL_QUERY)
        unified_graph.update_vertices(alarms)

        json_graph = unified_graph.json_output_graph(
            inspected_index=self._find_rca_index(unified_graph, root))

        return json_graph

    def _get_rca_for_specific_project(self,
                                      ga,
                                      found_graph_in,
                                      found_graph_out,
                                      root,
                                      project_id,
                                      is_admin_project):
        """Filter the RCA for root entity with consideration of project_id

        Filter the RCA for root by:
        1. filter the alarms deduced from the root alarm (found_graph_in)
        2. filter the alarms caused the root alarm (found_graph_out)
        And in the end unify 1 and 2

        :type ga: NXAlgorithm
        :type found_graph_in: NXGraph
        :type found_graph_out: NXGraph
        :type root: string
        :type project_id: string
        :type is_admin_project: boolean
        :rtype: NXGraph
        """

        filtered_alarms_out = \
            self._filter_alarms(found_graph_out.get_vertices(), project_id)
        filtered_found_graph_out = ga.subgraph(
            [node.vertex_id for node in filtered_alarms_out])
        filtered_found_graph_in = \
            self._filter_rca_causing_entities(ga,
                                              found_graph_in,
                                              root,
                                              project_id,
                                              is_admin_project)
        filtered_found_graph_out.union(filtered_found_graph_in)

        return filtered_found_graph_out

    def _filter_rca_causing_entities(self,
                                     ga,
                                     rca_graph,
                                     root_id,
                                     project_id,
                                     is_admin_project):
        """Filter the RCA entities which caused this alarm

        Shows only the causing alarms which has the same project_id and also
        the first alarm that has a different project_id. In case the tenant is
        admin then project_id can also be None.

        :type ga: NXAlgorithm
        :type rca_graph: NXGraph
        :type root_id: string
        :type project_id: string
        :type is_admin_project: boolean
        :rtype: NXGraph
        """

        entities = [root_id]
        current_entity_id = root_id

        while len(rca_graph.neighbors(current_entity_id,
                                      direction=Direction.IN)) > 0:
            current_entity = rca_graph.neighbors(current_entity_id,
                                                 direction=Direction.IN)[0]
            current_entity_id = current_entity.vertex_id
            entities.append(current_entity.vertex_id)
            if not self._is_alarm_of_current_project(current_entity,
                                                     project_id,
                                                     is_admin_project):
                break

        return ga.subgraph(entities)

    @staticmethod
    def _find_rca_index(found_graph, root):
        for root_index, vertex in enumerate(found_graph._g):
            if vertex == root:
                return root_index
        return 0
