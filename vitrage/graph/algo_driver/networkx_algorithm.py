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

from networkx.algorithms import components
from networkx.algorithms import simple_paths

from oslo_log import log as logging

from vitrage.common.constants import EdgeProperties as EProps
from vitrage.graph.algo_driver.algorithm import GraphAlgorithm
from vitrage.graph.algo_driver.algorithm import Mapping
from vitrage.graph.algo_driver.sub_graph_matching import NEG_CONDITION
from vitrage.graph.algo_driver.sub_graph_matching import subgraph_matching
from vitrage.graph.driver import Direction
from vitrage.graph.driver import Edge
from vitrage.graph.driver import Vertex
from vitrage.graph.filter import check_filter
from vitrage.graph.query import create_predicate
import requests
import ast
import json


LOG = logging.getLogger(__name__)


class NXAlgorithm(GraphAlgorithm):

    def __init__(self, graph):
        """Create a new GraphAlgorithm

        :param graph: graph instance
        :type graph: driver.Graph
        """
        super(NXAlgorithm, self).__init__(graph)

    @classmethod
    def _create_new_graph(cls, *args, **kwargs):
        LOG.info("###############This is graph/algo_driver/networkx_algorithm.py ############ ")
        LOG.info("############### STEP 6 ############ ")
        LOG.info('##### ARGS %r',args)
        LOG.info('##### KWARGS %r ',kwargs)
        from vitrage.graph.driver.networkx_graph import NXGraph
        return NXGraph(args, **kwargs)

    def graph_query_vertices(self,
                             root_id,
                             query_dict=None,
                             depth=None,
                             direction=Direction.BOTH,
                             edge_query_dict=None):
        graph = self._create_new_graph('graph')

        root_data = self.graph._g.node[root_id]

        match_func = create_predicate(query_dict) if query_dict else None
        edge_match_func = create_predicate(edge_query_dict) \
            if edge_query_dict else None

        if match_func and not match_func(root_data):
            LOG.info('graph_query_vertices: root %s does not match filter %s',
                     str(root_id), str(query_dict))
            return graph

        n_result = []
        visited_nodes = set()
        n_result.append((root_id, self.graph.get_vertex(root_id).properties))
        e_result = []
        nodes_q = [(root_id, 0)]
        while nodes_q:
            node_id, curr_depth = nodes_q.pop(0)
            if (node_id in visited_nodes) or (depth and curr_depth >= depth):
                continue
            visited_nodes.add(node_id)
            (n_list, e_list) = self.graph._neighboring_nodes_edges_query(
                node_id,
                direction=direction,
                vertex_predicate=match_func,
                edge_predicate=edge_match_func)
            n_result.extend(n_list)
            e_result.extend(e_list)
            nodes_q.extend([(v_id, curr_depth + 1) for v_id, data in n_list])

        graph = self._create_new_graph(
            graph.name,
            vertices=self._vertex_result_to_list(n_result),
            edges=self._edge_result_to_list(e_result))

        LOG.debug('graph_query_vertices: find graph: nodes %s, edges %s',
                  str(list(graph._g.nodes(data=True))),
                  str(list(graph._g.edges(data=True))))
        LOG.debug('graph_query_vertices: real graph: nodes %s, edges %s',
                  str(list(self.graph._g.nodes(data=True))),
                  str(list(self.graph._g.edges(data=True))))
        return graph

    def sub_graph_matching(self,
                           subgraph,
                           known_match,
                           validate=False):
        """Finds all the matching subgraphs in the graph

        In case the known_match has a subgraph edge with property
        "negative_condition" then run subgraph matching on the edge vertices
        and unite the results.
        Otherwise just run subgraph matching and return its result.

        :param subgraph: the subgraph to match
        :param known_match: starting point at the subgraph and the graph
        :param validate:
        :return: all the matching subgraphs in the graph
        """
        sge = known_match.subgraph_element
        ge = known_match.graph_element

        if not known_match.is_vertex and sge.get(NEG_CONDITION):
            source_matches = self._filtered_subgraph_matching(ge.source_id,
                                                              sge.source_id,
                                                              subgraph,
                                                              validate)
            target_matches = self._filtered_subgraph_matching(ge.target_id,
                                                              sge.target_id,
                                                              subgraph,
                                                              validate)

            return self._list_union(source_matches, target_matches)
        else:
            return subgraph_matching(self.graph,
                                     subgraph,
                                     [known_match],
                                     validate)

    def create_graph_from_matching_vertices(self,
                                            vertex_attr_filter=None,
                                            query_dict=None,
                                            edge_attr_filter=None):
        LOG.info("###############This is graph/algo_driver/networkx_algorithm.py ############ ")
        LOG.info("############### STEP 5 ############ ")
        LOG.info("vertex_attr_filter %r",vertex_attr_filter)
        LOG.info("query_dict %r",query_dict)
        LOG.info("edge_attr_filter %r",edge_attr_filter)


        if query_dict:
            vertices = self.graph.get_vertices(query_dict=query_dict)
        elif vertex_attr_filter:
            vertices = self.graph.get_vertices(
                vertex_attr_filter=vertex_attr_filter)
        else:
            vertices = self.graph.get_vertices()

        # LOG.info("vertices %r", vertices)
        # LOG.info("vertices %r", type(vertices))

        # data = requests.get('http://192.168.11.101:7071/MECrca')
                # real = ast.literal_eval(json.loads(data.json()))
        # real = json.loads(data.json())

        # LOG.info("vertices22222222 %r", real)
        vertices_ids = [vertex.vertex_id for vertex in vertices]

        # LOG.info("vertices22222222 %r", data)

        """
        graph => create base graph
        graph => self._g = nx.MultiDiGraph()  <networkx.classes.multidigraph.MultiDiGraph>

        """

        graph = self._create_new_graph('graph')
        LOG.info("############### STEP 11 ############ ")

        LOG.info("### vertices %r", vertices_ids)
        graph._g = self.graph._g.subgraph(vertices_ids).copy()
        LOG.info("### graph._g %r",graph._g)

        # delete non matching edges
        if edge_attr_filter:
            self._apply_edge_attr_filter(graph, edge_attr_filter)

        LOG.debug('match query, find graph: nodes %s, edges %s',
                  str(list(graph._g.nodes(data=True))),
                  str(list(graph._g.edges(data=True))))
        LOG.debug('match query, real graph: nodes %s, edges %s',
                  str(list(self.graph._g.nodes(data=True))),
                  str(list(self.graph._g.edges(data=True))))

        # url = 'http://192.168.11.101:7071/MECrcaagent'
        # response = requests.get(url)
        # LOG.info("graph %r", response.text)
        # LOG.info("graph type %r", type(response.text))
        # return response.text
        LOG.info("GRAPH %r",graph)
        LOG.info("GRAPH TYPE %r",type(graph))
        return graph

    def subgraph(self, entities):
        LOG.info("############### STEP 12 ############ ")
        subgraph = self._create_new_graph('graph')
        LOG.info("############### STEP 13 ############ ")
        subgraph._g = self.graph._g.subgraph(entities)
        return subgraph

    def connected_component_subgraphs(self, subgraph):
        return components.connected_component_subgraphs(
            subgraph._g.to_undirected(), copy=False)

    def all_simple_paths(self, source, target):
        return simple_paths.all_simple_paths(self.graph._g,
                                             source=source,
                                             target=target)

    def _filtered_subgraph_matching(self,
                                    ge_v_id,
                                    sge_v_id,
                                    subgraph,
                                    validate):
        """Runs subgraph_matching on edges vertices with filtering

        Runs subgraph_matching on edges vertices after checking if that vertex
        has real neighbors in the entity graph.
        """
        if self.graph.neighbors(ge_v_id,
                                edge_attr_filter={EProps.VITRAGE_IS_DELETED:
                                                  False}):
            template_vertex = subgraph.get_vertex(sge_v_id)
            graph_vertex = self.graph.get_vertex(ge_v_id)
            match = Mapping(template_vertex, graph_vertex, True)
            return subgraph_matching(self.graph, subgraph, [match], validate)

        return []

    @staticmethod
    def _edge_result_to_list(edge_result):
        d = dict()
        for source_id, target_id, label, data in edge_result:
            d[(source_id, target_id, label)] = \
                Edge(source_id, target_id, label, properties=data)
        return d.values()

    @staticmethod
    def _vertex_result_to_list(vertex_result):
        d = dict()
        for v_id, data in vertex_result:
            d[v_id] = Vertex(vertex_id=v_id, properties=data)
        return d.values()

    @staticmethod
    def _list_union(list_1, list_2):
        """Union of list that aren't hashable

        Can't use here set union because the items in the lists are
        dictionaries and they are not hashable for set.

        :return: list - union list
        """

        for target_item in list_2:
            if target_item not in list_1:
                list_1.append(target_item)

        return list_1

    @staticmethod
    def _apply_edge_attr_filter(graph, edge_attr_filter):
        edges = graph._g.edges(data=True, keys=True)
        edges_to_remove = [(u, v, k) for (u, v, k, d) in edges
                           if not check_filter(d, edge_attr_filter)]
        for source, target, key in edges_to_remove:
            graph._g.remove_edge(u=source, v=target, key=key)
