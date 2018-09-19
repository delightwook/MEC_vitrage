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
from testtools import matchers

from vitrage.entity_graph.mappings.operational_resource_state import \
    OperationalResourceState

from vitrage.common.constants import VertexProperties as VProps
from vitrage.evaluator.actions.base import ActionType
from vitrage.evaluator.actions.recipes.action_steps import UPDATE_VERTEX
from vitrage.evaluator.actions.recipes.set_state import SetState
from vitrage.evaluator.template_data import ActionSpecs
from vitrage.evaluator.template_fields import TemplateFields as TFields
from vitrage.graph import Vertex
from vitrage.tests import base

_SET_STATES_PARAM_LEN = 3


class SetStateRecipeTest(base.BaseTest):

    # noinspection PyPep8Naming
    @classmethod
    def setUpClass(cls):
        super(SetStateRecipeTest, cls).setUpClass()

        cls.target_vertex = Vertex('RESOURCE:nova.host:test1')

        targets = {TFields.TARGET: cls.target_vertex}
        cls.props = {TFields.STATE: OperationalResourceState.SUBOPTIMAL}

        cls.action_spec = ActionSpecs(
            0, ActionType.SET_STATE, targets, cls.props)

    def test_get_do_recipe(self):

        # Test Action
        action_steps = SetState.get_do_recipe(self.action_spec)

        # Test Assertions

        # expecting for one step: [update_vertex]
        self.assertThat(action_steps, matchers.HasLength(1))

        self.assertEqual(UPDATE_VERTEX, action_steps[0].type)
        update_vertex_step_params = action_steps[0].params
        self.assertThat(update_vertex_step_params,
                        matchers.HasLength(_SET_STATES_PARAM_LEN))

        vitrage_state = update_vertex_step_params[VProps.VITRAGE_STATE]
        self.assertEqual(self.props[TFields.STATE], vitrage_state)

        vitrage_id = update_vertex_step_params[VProps.VITRAGE_ID]
        self.assertEqual(self.target_vertex.vertex_id, vitrage_id)

    def test_get_undo_recipe(self):

        # Test Action
        action_steps = SetState.get_undo_recipe(self.action_spec)

        # Test Assertions

        # expecting for one step: [update_vertex]
        self.assertThat(action_steps, matchers.HasLength(1))

        self.assertEqual(UPDATE_VERTEX, action_steps[0].type)
        update_vertex_step_params = action_steps[0].params
        self.assertThat(update_vertex_step_params,
                        matchers.HasLength(_SET_STATES_PARAM_LEN))

        vitrage_state = update_vertex_step_params[VProps.VITRAGE_STATE]
        self.assertIsNone(vitrage_state)

        vitrage_id = update_vertex_step_params[VProps.VITRAGE_ID]
        self.assertEqual(self.target_vertex.vertex_id, vitrage_id)
