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

from testtools.matchers import HasLength
from vitrage.evaluator.actions.base import ActionType
from vitrage.evaluator.actions.recipes.action_steps import EXECUTE_EXTERNAL
from vitrage.evaluator.actions.recipes.action_steps import EXECUTION_ENGINE
from vitrage.evaluator.actions.recipes.execute_mistral import ExecuteMistral
from vitrage.evaluator.actions.recipes.execute_mistral import MISTRAL
from vitrage.evaluator.actions.recipes.execute_mistral import WORKFLOW
from vitrage.evaluator.template_data import ActionSpecs
from vitrage.tests.base import BaseTest
from vitrage.tests.base import IsEmpty


class RaiseAlarmRecipeTest(BaseTest):

    # noinspection PyPep8Naming
    @classmethod
    def setUpClass(cls):
        super(RaiseAlarmRecipeTest, cls).setUpClass()
        cls.props = {EXECUTION_ENGINE: MISTRAL,
                     WORKFLOW: 'wf_4',
                     'host': 'host5',
                     'state': 'ok'}
        cls.action_spec = ActionSpecs(0,
                                      ActionType.EXECUTE_MISTRAL,
                                      {},
                                      cls.props)

    def test_get_do_recipe(self):

        # Test Action
        action_steps = ExecuteMistral.get_do_recipe(self.action_spec)

        # Test Assertions

        # expecting for one step: [execute_external]
        self.assertThat(action_steps, HasLength(1))

        self.assertEqual(EXECUTE_EXTERNAL, action_steps[0].type)
        execute_external_step_params = action_steps[0].params
        self.assertIsNotNone(execute_external_step_params)
        self.assertLessEqual(2, len(execute_external_step_params))

        execution_engine = execute_external_step_params[EXECUTION_ENGINE]
        self.assertEqual(self.props[EXECUTION_ENGINE], execution_engine)

        workflow = execute_external_step_params[WORKFLOW]
        self.assertEqual(self.props[WORKFLOW], workflow)

    def test_get_undo_recipe(self):

        # Test Action
        action_steps = ExecuteMistral.get_undo_recipe(self.action_spec)

        # Test Assertions

        # expecting for zero steps (no undo for this action)
        self.assertThat(action_steps, IsEmpty())
