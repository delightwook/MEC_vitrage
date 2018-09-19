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

from vitrage.common.constants import VertexProperties as VProps
from vitrage.datasources.alarm_properties import AlarmProperties
from vitrage.datasources.nova.host import NOVA_HOST_DATASOURCE
from vitrage.evaluator.actions.base import ActionType
from vitrage.evaluator.actions.recipes.action_steps import ADD_VERTEX
from vitrage.evaluator.actions.recipes.action_steps import REMOVE_VERTEX
from vitrage.evaluator.actions.recipes.raise_alarm import RaiseAlarm
from vitrage.evaluator.template_data import ActionSpecs
from vitrage.evaluator.template_fields import TemplateFields as TFields
from vitrage.graph import Vertex
from vitrage.tests import base


class RaiseAlarmRecipeTest(base.BaseTest):

    # noinspection PyPep8Naming
    @classmethod
    def setUpClass(cls):
        super(RaiseAlarmRecipeTest, cls).setUpClass()
        cls.target_props = {VProps.VITRAGE_TYPE: NOVA_HOST_DATASOURCE}
        cls.target_vertex = Vertex('RESOURCE:nova.host:test1',
                                   cls.target_props)
        cls.targets = {TFields.TARGET: cls.target_vertex}
        cls.props = {TFields.ALARM_NAME: 'VM_CPU_SUBOPTIMAL_PERFORMANCE'}

        cls.action_spec = ActionSpecs(
            0, ActionType.SET_STATE, cls.targets, cls.props)

    def test_get_do_recipe(self):

        # Test Action
        action_steps = RaiseAlarm.get_do_recipe(self.action_spec)

        # Test Assertions

        # expecting for one step: [add_vertex]
        self.assertThat(action_steps, matchers.HasLength(1))

        self.assertEqual(ADD_VERTEX, action_steps[0].type)
        add_vertex_step_params = action_steps[0].params
        self.assertThat(add_vertex_step_params, matchers.HasLength(4))

        alarm_name = add_vertex_step_params[TFields.ALARM_NAME]
        self.assertEqual(self.props[TFields.ALARM_NAME], alarm_name)

        target_vitrage_id = add_vertex_step_params[TFields.TARGET]
        self.assertEqual(self.target_vertex.vertex_id, target_vitrage_id)

        alarm_state = add_vertex_step_params[TFields.STATE]
        self.assertEqual(alarm_state, AlarmProperties.ACTIVE_STATE)

        alarm_vitrage_resource_type = \
            add_vertex_step_params[VProps.VITRAGE_RESOURCE_TYPE]
        self.assertEqual(self.target_vertex.properties[VProps.VITRAGE_TYPE],
                         alarm_vitrage_resource_type)

    def test_get_undo_recipe(self):

        # Test Action
        action_steps = RaiseAlarm.get_undo_recipe(self.action_spec)

        # Test Assertions

        # expecting for one step: [remove_vertex]
        self.assertThat(action_steps, matchers.HasLength(1))

        self.assertEqual(REMOVE_VERTEX, action_steps[0].type)
        remove_vertex_step_params = action_steps[0].params

        # remove_vertex expects four params: alarm name, state, target,
        # and type
        self.assertThat(remove_vertex_step_params, matchers.HasLength(4))

        alarm_name = remove_vertex_step_params[TFields.ALARM_NAME]
        self.assertEqual(self.props[TFields.ALARM_NAME], alarm_name)

        target_vitrage_id = remove_vertex_step_params[TFields.TARGET]
        self.assertEqual(self.target_vertex.vertex_id, target_vitrage_id)

        alarm_state = remove_vertex_step_params[TFields.STATE]
        self.assertEqual(alarm_state, AlarmProperties.INACTIVE_STATE)

        alarm_vitrage_resource_type = \
            remove_vertex_step_params[VProps.VITRAGE_RESOURCE_TYPE]
        self.assertEqual(self.target_vertex.properties[VProps.VITRAGE_TYPE],
                         alarm_vitrage_resource_type)
