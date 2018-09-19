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
import abc

from vitrage.evaluator.actions.base import ActionType
from vitrage.evaluator.actions.recipes.execute_mistral import WORKFLOW
from vitrage.evaluator.template_fields import TemplateFields
from vitrage.tests.unit.evaluator.template_validation.content.base import \
    ActionValidatorTest
from vitrage.tests.unit.evaluator.template_validation.content.base import \
    DEFINITIONS_INDEX_MOCK


class BaseExecuteMistralValidatorTest(ActionValidatorTest):

    @abc.abstractmethod
    def _create_execute_mistral_action(self, workflow, host, host_state):
        pass

    def _validate_execute_mistral_action(self, validator):
        self._validate_action(
            self._create_execute_mistral_action('wf_1', 'host_2', 'down'),
            validator.validate
        )

    def _validate_execute_mistral_action_without_workflow(self, validator):

        # Test setup
        idx = DEFINITIONS_INDEX_MOCK.copy()
        action = self._create_execute_mistral_action('wf_1', 'host_2', 'down')
        action[TemplateFields.PROPERTIES].pop(WORKFLOW)

        # Test action
        result = validator.validate(action, idx)

        # Test assertions
        self._assert_fault_result(result, 133)

    def _validate_execute_mistral_action_with_empty_workflow(self, validator):

        # Test setup
        idx = DEFINITIONS_INDEX_MOCK.copy()
        action = self._create_execute_mistral_action('', 'host_2', 'down')

        # Test action
        result = validator.validate(action, idx)

        # Test assertions
        self._assert_fault_result(result, 133)

    def _validate_execute_mistral_action_with_none_workflow(self, validator):

        # Test setup
        idx = DEFINITIONS_INDEX_MOCK.copy()
        action = self._create_execute_mistral_action(None, 'host_2', 'down')

        # Test action
        result = validator.validate(action, idx)

        # Test assertions
        self._assert_fault_result(result, 133)

    def _validate_execute_mistral_action_without_additional_props(self,
                                                                  validator):

        # Test setup - having only the 'workflow' param is a legal config
        idx = DEFINITIONS_INDEX_MOCK.copy()
        action = self._create_no_input_mistral_action('wf_1')

        # Test action
        result = validator.validate(action, idx)

        # Test assertions
        self._assert_correct_result(result)

    @staticmethod
    def _create_no_input_mistral_action(workflow):

        properties = {
            WORKFLOW: workflow,
        }
        action = {
            TemplateFields.ACTION_TYPE: ActionType.EXECUTE_MISTRAL,
            TemplateFields.PROPERTIES: properties
        }

        return action

    @staticmethod
    def _create_v1_execute_mistral_action(workflow, host, host_state,
                                          **kwargs):

        properties = {
            WORKFLOW: workflow,
            'host': host,
            'host_state': host_state
        }
        properties.update(kwargs)

        action = {
            TemplateFields.ACTION_TYPE: ActionType.EXECUTE_MISTRAL,
            TemplateFields.PROPERTIES: properties
        }

        return action

    @staticmethod
    def _create_v2_execute_mistral_action(workflow, host, host_state,
                                          **kwargs):

        input_props = {
            'host': host,
            'host_state': host_state
        }
        input_props.update(kwargs)
        properties = {
            WORKFLOW: workflow,
            'input': input_props
        }

        action = {
            TemplateFields.ACTION_TYPE: ActionType.EXECUTE_MISTRAL,
            TemplateFields.PROPERTIES: properties
        }

        return action
