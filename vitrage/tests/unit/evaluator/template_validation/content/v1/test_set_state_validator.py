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

from vitrage.entity_graph.mappings.operational_resource_state import \
    OperationalResourceState
from vitrage.evaluator.actions.base import ActionType
from vitrage.evaluator.template_fields import TemplateFields
from vitrage.evaluator.template_validation.content.v1.set_state_validator \
    import SetStateValidator
from vitrage.tests.unit.evaluator.template_validation.content.base import \
    ActionValidatorTest
from vitrage.tests.unit.evaluator.template_validation.content.base import \
    DEFINITIONS_INDEX_MOCK


class SetStateValidatorTest(ActionValidatorTest):

    def test_validate_set_state_action(self):

        self._validate_action(self._create_set_state_action('123'),
                              SetStateValidator.validate)

    def test_validate_set_state_action_without_action_target(self):

        self._validate_action_without_action_target(
            self._create_set_state_action('123'),
            SetStateValidator.validate
        )

    def test_validate_set_state_action_with_invalid_target_id(self):

        self._validate_action_with_invalid_target_id(
            self._create_set_state_action('unknown'),
            SetStateValidator.validate
        )

    def test_validate_set_state_action_without_target_id(self):

        self._validate_action_without_target_id(
            self._create_set_state_action('123'),
            SetStateValidator.validate,
            129
        )

    def test_validate_set_state_action_without_state_property(self):

        # Test setup
        idx = DEFINITIONS_INDEX_MOCK.copy()
        action = self._create_set_state_action('123')
        action[TemplateFields.PROPERTIES].pop(TemplateFields.STATE, None)

        # Test action
        result = SetStateValidator.validate(action, idx)

        # Test assertions
        self._assert_fault_result(result, 128)

    @staticmethod
    def _create_set_state_action(target):

        action_target = {
            TemplateFields.TARGET: target
        }
        properties = {
            TemplateFields.STATE: OperationalResourceState.SUBOPTIMAL
        }
        action = {
            TemplateFields.ACTION_TYPE: ActionType.SET_STATE,
            TemplateFields.ACTION_TARGET: action_target,
            TemplateFields.PROPERTIES: properties
        }
        return action
