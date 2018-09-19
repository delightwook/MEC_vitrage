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
from vitrage.evaluator.template_validation.content.v2.\
    execute_mistral_validator import ExecuteMistralValidator as \
    V2ExecuteMistralValidator
from vitrage.tests.unit.evaluator.template_validation.content.\
    base_test_execute_mistral_validator import BaseExecuteMistralValidatorTest
from vitrage.tests.unit.evaluator.template_validation.content.base import \
    DEFINITIONS_INDEX_MOCK


class ExecuteMistralValidatorTest(BaseExecuteMistralValidatorTest):

    @classmethod
    def setUpClass(cls):
        super(ExecuteMistralValidatorTest, cls).setUpClass()
        cls.validator = V2ExecuteMistralValidator()

    def test_v2_validate_execute_mistral_action(self):
        self._validate_execute_mistral_action(self.validator)

    def test_v2_validate_old_execute_mistral_action(self):
        """Test version2 validator on version1 template.

        An execute_mistral action from version 1 should fail in the validation
        of version 2.
        """

        # Test setup
        idx = DEFINITIONS_INDEX_MOCK.copy()
        v1_action = \
            self._create_v1_execute_mistral_action('wf_1', 'host_2', 'down')

        # Test action
        result = self.validator.validate(v1_action, idx)

        # Test assertions
        self._assert_fault_result(result, 136)

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

    def test_v2_validate_execute_mistral_action_with_func(self):
        self._validate_action(
            self._create_v2_execute_mistral_action(
                'wf_1', 'host_2', 'down', func1='get_attr(alarm,name)'),
            self.validator.validate
        )

    def test_v2_validate_execute_mistral_action_with_func_2(self):
        self._validate_action(
            self._create_v2_execute_mistral_action(
                'wf_1', 'host_2', 'down', func1='get_attr(alarm, name)'),
            self.validator.validate
        )

    def test_v2_validate_execute_mistral_action_with_func_3(self):
        self._validate_action(
            self._create_v2_execute_mistral_action(
                'wf_1', 'host_2', 'down', func1='get_attr ( alarm , name ) '),
            self.validator.validate
        )

    def test_v2_validate_execute_mistral_action_with_func_typo_1(self):
        # Test setup
        idx = DEFINITIONS_INDEX_MOCK.copy()
        action = \
            self._create_v2_execute_mistral_action(
                'wf_1', 'host_2', 'down', func1='get_attr(alarm, name')

        # Test action
        result = self.validator.validate(action, idx)

        # Test assertions
        self._assert_warning_result(result, 138)

    def test_v2_validate_execute_mistral_action_with_func_typo_2(self):
        # Test setup
        idx = DEFINITIONS_INDEX_MOCK.copy()
        action = \
            self._create_v2_execute_mistral_action(
                'wf_1', 'host_2', 'down', func1='get_attr, name)')

        # Test action
        result = self.validator.validate(action, idx)

        # Test assertions
        self._assert_warning_result(result, 138)

    def _create_execute_mistral_action(self, workflow, host, host_state):
        return self.\
            _create_v2_execute_mistral_action(workflow, host, host_state)
