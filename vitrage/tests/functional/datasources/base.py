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

from vitrage.common.constants import EntityCategory
from vitrage.common.constants import VertexProperties as VProps
from vitrage.tests.functional.base import TestFunctionalBase


class TestDataSourcesBase(TestFunctionalBase):

    def _find_entity_id_by_type(self, graph, vitrage_type):
        entity_vertices = graph.get_vertices(vertex_attr_filter={
            VProps.VITRAGE_CATEGORY: EntityCategory.RESOURCE,
            VProps.VITRAGE_TYPE: vitrage_type
        })
        self.assertGreater(len(entity_vertices), 0)

        return entity_vertices[0][VProps.ID]
