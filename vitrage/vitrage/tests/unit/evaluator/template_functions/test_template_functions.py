# Copyright 2018 - Nokia
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

from vitrage.evaluator.template_functions.v2.functions import get_attr
from vitrage.graph.driver import Vertex
from vitrage.tests import base


class TemplateFunctionsTest(base.BaseTest):

    def test_get_attr_with_existing_attr(self):
        entity_id = 'id1234'
        match = self._create_match('instance', properties={'id': entity_id})

        attr = get_attr(match, 'instance', 'id')
        self.assertIsNotNone(attr)
        self.assertEqual(entity_id, attr)

    def test_get_attr_with_non_existing_attr(self):
        match = self._create_match('instance', properties={'id': 'id1'})
        attr = get_attr(match, 'instance', 'non_existing_attr')
        self.assertIsNone(attr)

    def test_get_attr_with_two_attrs(self):
        properties = {'attr1': 'first_attr', 'attr2': 'second_attr'}
        match = self._create_match('instance', properties)

        attr = get_attr(match, 'instance', 'attr1')
        self.assertIsNotNone(attr)
        self.assertEqual('first_attr', attr)

        attr = get_attr(match, 'instance', 'attr2')
        self.assertIsNotNone(attr)
        self.assertEqual('second_attr', attr)

        attr = get_attr(match, 'instance', 'attr3')
        self.assertIsNone(attr)

    def test_get_attr_with_non_existing_entity(self):
        match = self._create_match('instance', properties={'attr1': 'attr1'})
        attr = get_attr(match, 'non_existing_entity', 'attr1')
        self.assertIsNone(attr)

    @staticmethod
    def _create_match(template_id, properties):
        entity = Vertex(vertex_id='f89fe840-b595-4010-8a09-a444c7642865',
                        properties=properties)
        return {template_id: entity}
