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
from vitrage.api_handler.apis.base import TOPOLOGY_AND_ALARMS_QUERY
from vitrage.common.constants import EdgeProperties as EProps
from vitrage.common.constants import EntityCategory
from vitrage.common.constants import TenantProps
from vitrage.common.constants import VertexProperties as VProps
from vitrage.common.exception import VitrageError
from vitrage.datasources.nova.instance import NOVA_INSTANCE_DATASOURCE
from vitrage.datasources import OPENSTACK_CLUSTER

LOG = log.getLogger(__name__)


@profiler.trace_cls("topology apis",
                    info={}, hide_args=False, trace_private=False)
class TopologyApis(EntityGraphApisBase):

    def __init__(self, entity_graph, conf):
        self.entity_graph = entity_graph
        self.conf = conf

    def get_topology(self, ctx, graph_type, depth, query, root, all_tenants):
        LOG.info("###############This is apis/topology.py ############ ")
        LOG.info("############### STEP 1 ############ ")
        LOG.info("ctx %r",ctx)
        LOG.info("graph_type %r", graph_type)
        LOG.info("depth %r", depth)
        LOG.info("query %r", query)
        LOG.info("root %r", root)
        LOG.info("all_tenants %r", all_tenants)

        LOG.debug("TopologyApis get_topology - root: %s, all_tenants=%s",
                  str(root), all_tenants)

        project_id = ctx.get(TenantProps.TENANT, None)
        is_admin_project = ctx.get(TenantProps.IS_ADMIN, False)
        ga = self.entity_graph.algo

        LOG.debug('project_id = %s, is_admin_project  %s',
                  project_id, is_admin_project)

        root_id = root or self._default_root_id()
        if graph_type == 'tree' or \
                ((root is not None) and (depth is not None)):
            if not query:
                LOG.error("Graph-type 'tree' requires a filter.")
                raise Exception("Graph-type 'tree' requires a filter.")

            current_query = query
            if not all_tenants:
                project_query = \
                    {'or': [{'==': {VProps.PROJECT_ID: project_id}},
                            {'==': {VProps.PROJECT_ID: None}}]}
                current_query = {'and': [query, project_query]}

            graph = ga.graph_query_vertices(root_id,
                                            query_dict=current_query,
                                            depth=depth,
                                            edge_query_dict=EDGE_QUERY)

        # By default the graph_type is 'graph'
        else:
            LOG.info("###############This is apis/topology.py ############ ")
            LOG.info("############### STEP 2 ############ ")
            LOG.info("VProps.PROJECT_ID %r", VProps.PROJECT_ID)
            if all_tenants:
                q = query if query else TOPOLOGY_AND_ALARMS_QUERY
                graph = ga.create_graph_from_matching_vertices(
                    query_dict=q,
                    edge_attr_filter={VProps.VITRAGE_IS_DELETED: False})
            else:
                graph = self._get_topology_for_specific_project(
                    ga,
                    query,
                    project_id,
                    is_admin_project,
                    root_id)
                """
                Graph is vitrage.graph.driver.networkx_graph.NXGraph
                """
                LOG.info("graph %r", graph)

        return graph.json_output_graph()

    def _get_topology_for_specific_project(self,
                                           ga,
                                           query,
                                           project_id,
                                           is_admin_project,
                                           root):
        """Finds the topology in consideration with the project_id

        Finds all the entities which has project_id. In case the tenant is
        admin then project_id can also be None.

        :type ga: NXAlgorithm
        :type query: dictionary
        :type project_id: string
        :type is_admin_project: boolean
        :type root: string
        :rtype: NXGraph
        """

        if query:
            LOG.info("###############This is apis/topology.py ############ ")
            LOG.info("############### STEP 3(if) ############ ")
            q = self._add_project_to_query(query, project_id, is_admin_project)
        else:
            LOG.info("###############This is apis/topology.py ############ ")
            LOG.info("############### STEP 3(else) ############ ")
            alarm_query = self._get_query_with_project(EntityCategory.ALARM,
                                                       project_id,
                                                       is_admin=True)

            resource_query = \
                self._get_query_with_project(EntityCategory.RESOURCE,
                                             project_id,
                                             is_admin_project)

            default_query = {'or': [resource_query, alarm_query]}
            q = default_query

        tmp_graph = ga.create_graph_from_matching_vertices(query_dict=q)
        LOG.info("###############This is api_handler/api/topology.py ############ ")
        LOG.info("############### STEP 9 ############ ")
        LOG.info("### tmp_graph %r",tmp_graph)
        graph = self._create_graph_of_connected_components(ga, tmp_graph, root)
        edge_query = {EProps.VITRAGE_IS_DELETED: False}
        self._remove_unnecessary_elements(ga,
                                          graph,
                                          project_id,
                                          is_admin_project,
                                          edge_attr_filter=edge_query)

        return graph

    def _remove_unnecessary_elements(self,
                                     ga,
                                     graph,
                                     project_id,
                                     is_admin_project,
                                     edge_attr_filter):
        # delete non matching edges
        ga._apply_edge_attr_filter(graph, edge_attr_filter)

        self._remove_alarms_of_other_projects(graph,
                                              project_id,
                                              is_admin_project)

    def _remove_alarms_of_other_projects(self,
                                         graph,
                                         current_project_id,
                                         is_admin_project):
        """Removes wrong alarms from the graph

        Removes alarms of other tenants from the graph, In case the tenant is
        admin then project_id can also be None.

        :type graph: NXGraph
        :type current_project_id: string
        :type is_admin_project: boolean
        """

        for alarm in graph.get_vertices(query_dict=ALARMS_ALL_QUERY):
            if not alarm.get(VProps.PROJECT_ID, None):
                cat_filter = {VProps.VITRAGE_CATEGORY: EntityCategory.RESOURCE}
                resource_neighbors = \
                    self.entity_graph.neighbors(alarm.vertex_id,
                                                vertex_attr_filter=cat_filter)
                if len(resource_neighbors) > 0:
                    resource_proj_id = \
                        resource_neighbors[0].get(VProps.PROJECT_ID, None)
                    cond1 = is_admin_project and resource_proj_id and \
                        resource_proj_id != current_project_id
                    cond2 = not is_admin_project and \
                        (not resource_proj_id or
                         resource_proj_id != current_project_id)
                    if cond1 or cond2:
                        graph.remove_vertex(alarm)

    def _create_graph_of_connected_components(self, ga, tmp_graph, root):
        LOG.info("###############This is api_handler/api/topology.py ############ ")
        LOG.info("############### STEP 10 ############ ")
        LOG.info("### ga %r",ga)
        LOG.info("### tmp_graph %r", tmp_graph)
        LOG.info("### root %r", root)
        return ga.subgraph(self._topology_for_unrooted_graph(ga,
                                                             tmp_graph,
                                                             root)).copy()

    def _topology_for_unrooted_graph(self, ga, subgraph, root):
        """Finds topology for unrooted subgraph

        1. Finds all the connected component subgraphs in subgraph.
        2. For each component, finds the path from one of the VMs (if exists)
           to the root entity.
        3. Unify all the entities found and return them

        :type ga: NXAlgorithm
        :type subgraph: networkx graph
        :type root: string
        :rtype: list
        """

        entities = []

        root_vertex = \
            self.entity_graph.get_vertex(root)

        local_connected_component_subgraphs = \
            ga.connected_component_subgraphs(subgraph)

        for component_subgraph in local_connected_component_subgraphs:
            entities += list(component_subgraph.nodes())
            instance_in_component_subgraph = \
                self._find_instance_in_graph(component_subgraph)
            if instance_in_component_subgraph:
                paths = ga.all_simple_paths(root_vertex.vertex_id,
                                            instance_in_component_subgraph)
                for path in paths:
                    entities += path

        return set(entities)

    def _default_root_id(self):
        tmp_vertices = self.entity_graph.get_vertices(
            vertex_attr_filter={VProps.VITRAGE_TYPE: OPENSTACK_CLUSTER})
        if not tmp_vertices:
            LOG.debug("No root vertex found")
            return None
        if len(tmp_vertices) > 1:
            raise VitrageError("Multiple root vertices found")
        return tmp_vertices[0].vertex_id

    @staticmethod
    def _find_instance_in_graph(graph):
        for node, node_data in graph.nodes(data=True):
            if node_data[VProps.VITRAGE_CATEGORY] == \
                    EntityCategory.RESOURCE \
                    and node_data[VProps.VITRAGE_TYPE] == \
                    NOVA_INSTANCE_DATASOURCE:
                return node
        return None
