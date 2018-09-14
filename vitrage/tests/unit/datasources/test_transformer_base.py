# Copyright 2017 - Nokia
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

from vitrage.common.constants import VertexProperties as VProps
from vitrage.tests import base


# noinspection PyProtectedMember
class BaseTransformerTest(base.BaseTest):

    def _validate_base_vertex_props(self,
                                    vertex,
                                    expected_name,
                                    expected_datasource_name):
        self.assertFalse(vertex[VProps.VITRAGE_IS_PLACEHOLDER])
        self.assertEqual(expected_datasource_name, vertex[VProps.VITRAGE_TYPE])
        self.assertEqual(expected_name, vertex[VProps.NAME])
