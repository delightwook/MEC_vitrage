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
from vitrage.evaluator.template_fields import TemplateFields
from vitrage.evaluator.template_validation.content.v1.\
    execute_mistral_validator import ExecuteMistralValidator as \
    V1ExecuteMistralValidator
from vitrage.tests.unit.evaluator.template_validation.content.\
    base_test_execute_mistral_validator import BaseExecuteMistralValidatorTest
from vitrage.tests.unit.evaluator.template_validation.content.base import \
    DEFINITIONS_INDEX_MOCK


class ExecuteMistralValidatorTest(BaseExecuteMistralValidatorTest):

    @classmethod
    def setUpClass(cls):
        super(ExecuteMistralValidatorTest, cls).setUpClass()
        cls.validator = V1ExecuteMistralValidator()

    def test_v1_validate_execute_mistral_action(self):
        self._validate_execute_mistral_action(self.validator)

    def test_validate_execute_mistral_action_without_workflow(self):
        self._validate_execute_mistral_action_without_workflow(self.validator)

    def test_validate_execute_mistral_action_with_empty_workflow(self):
        self._validate_execute_mistral_action_with_empty_workflow(
            self.validator)

    def test_validate_execute_mistral_action_with_none_workflow(self):
        self._validate_execute_mistral_action_with_none_workflow(
            self.validator)

    def test_validate_execute_mistral_action_without_additional_props(self):
        self._validate_execute_mistral_action_without_additional_props(
            self.validator)

    def test_validate_execute_mistral_action_with_input_prop(self):
        """A version1 execute_mistral action can have an 'input' property"""

        # Test setup
        idx = DEFINITIONS_INDEX_MOCK.copy()
        action = self._create_execute_mistral_action('wf_1', 'host_2', 'down')
        action[TemplateFields.PROPERTIES]['input'] = 'kuku'

        # Test action
        result = self.validator.validate(action, idx)

        # Test assertions
        self._assert_correct_result(result)

    def test_validate_execute_mistral_action_with_input_dict(self):
        """A version1 execute_mistral action can have an 'input' dictionary"""

        # Test setup
        idx = DEFINITIONS_INDEX_MOCK.copy()
        action = self._create_execute_mistral_action('wf_1', 'host_2', 'down')
        input_dict = {'a': '1'}
        action[TemplateFields.PROPERTIES]['input'] = input_dict

        # Test action
        result = self.validator.validate(action, idx)

        # Test assertions
        self._assert_correct_result(result)

    def test_validate_execute_mistral_action_with_func(self):
        # Test setup
        idx = DEFINITIONS_INDEX_MOCK.copy()
        action = \
            self._create_v1_execute_mistral_action(
                'wf_1', 'host_2', 'down', func1='get_attr(alarm, name)')

        # Test action
        result = self.validator.validate(action, idx)

        # Test assertions
        self._assert_fault_result(result, 137)

    def _create_execute_mistral_action(self, workflow, host, host_state):
        return self.\
            _create_v1_execute_mistral_action(workflow, host, host_state)
