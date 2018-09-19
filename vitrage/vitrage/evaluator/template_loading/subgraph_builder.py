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

from vitrage.common.constants import EdgeProperties as EProps
from vitrage.common.constants import VertexProperties as VProps
from vitrage.evaluator.template_data import EdgeDescription
from vitrage.evaluator.template_data import ENTITY
from vitrage.graph.algo_driver.sub_graph_matching import NEG_CONDITION
from vitrage.graph.driver.networkx_graph import NXGraph


class SubGraphBuilder(object):
    @classmethod
    def from_condition(cls, condition, extract_var):
        return [cls.from_clause(clause, extract_var)
                for clause in condition]

    @classmethod
    def from_clause(cls, clause, extract_var):
        condition_g = NXGraph("scenario condition")

        for term in clause:
            variable, var_type = extract_var(term.symbol_name)
            if var_type == ENTITY:
                vertex = variable.copy()
                vertex[VProps.VITRAGE_IS_DELETED] = False
                vertex[VProps.VITRAGE_IS_PLACEHOLDER] = False
                condition_g.add_vertex(vertex)

            else:  # type = relationship
                # prevent overwritten of NEG_CONDITION and
                # VITRAGE_IS_DELETED property when there are both "not A"
                # and "A" in same template
                edge_desc = cls._copy_edge_desc(variable)
                cls._set_edge_relationship_info(edge_desc, term.positive)
                cls._add_edge_relationship(condition_g, edge_desc)

        return condition_g

    @staticmethod
    def _set_edge_relationship_info(edge_description,
                                    is_positive_condition):
        if not is_positive_condition:
            edge_description.edge[NEG_CONDITION] = True
            edge_description.edge[EProps.VITRAGE_IS_DELETED] = True
        else:
            edge_description.edge[EProps.VITRAGE_IS_DELETED] = False
            edge_description.edge[NEG_CONDITION] = False

        edge_description.source[VProps.VITRAGE_IS_DELETED] = False
        edge_description.source[VProps.VITRAGE_IS_PLACEHOLDER] = False
        edge_description.target[VProps.VITRAGE_IS_DELETED] = False
        edge_description.target[VProps.VITRAGE_IS_PLACEHOLDER] = False

    @staticmethod
    def _add_edge_relationship(condition_graph, edge_description):
        condition_graph.add_vertex(edge_description.source)
        condition_graph.add_vertex(edge_description.target)
        condition_graph.add_edge(edge_description.edge)

    @staticmethod
    def _copy_edge_desc(edge_desc):
        return EdgeDescription(edge=edge_desc.edge.copy(),
                               source=edge_desc.source.copy(),
                               target=edge_desc.target.copy())
