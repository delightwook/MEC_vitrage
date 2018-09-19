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

from vitrage.evaluator.actions.base import ActionType
from vitrage.evaluator.template_fields import TemplateFields
from vitrage.evaluator.template_validation.content.v1.raise_alarm_validator \
    import RaiseAlarmValidator
from vitrage.tests.unit.evaluator.template_validation.content.base import \
    ActionValidatorTest
from vitrage.tests.unit.evaluator.template_validation.content.base import \
    DEFINITIONS_INDEX_MOCK


class RaiseAlarmValidatorTest(ActionValidatorTest):

    def test_validate_raise_alarm_action(self):

        self._validate_action(self._create_raise_alarm_action('123'),
                              RaiseAlarmValidator.validate)

    def test_validate_raise_alarm_action_without_action_target(self):

        self._validate_action_without_action_target(
            self._create_raise_alarm_action('123'),
            RaiseAlarmValidator.validate
        )

    def test_raise_alarm_action_validate_invalid_target_id(self):

        self._validate_action_with_invalid_target_id(
            self._create_raise_alarm_action('unknown'),
            RaiseAlarmValidator.validate
        )

    def test_validate_raise_alarm_action_without_target_id(self):

        self._validate_action_without_target_id(
            self._create_raise_alarm_action('123'),
            RaiseAlarmValidator.validate,
            127
        )

    def test_validate_raise_alarm_action_without_severity(self):

        # Test setup
        idx = DEFINITIONS_INDEX_MOCK.copy()
        action = self._create_raise_alarm_action('abc')
        action[TemplateFields.PROPERTIES].pop(TemplateFields.SEVERITY)

        # Test action
        result = RaiseAlarmValidator.validate(action, idx)

        # Test assertions
        self._assert_fault_result(result, 126)

    def test_validate_raise_alarm_action_without_alarm_name(self):

        # Test setup
        idx = DEFINITIONS_INDEX_MOCK.copy()
        action = self._create_raise_alarm_action('abc')
        action[TemplateFields.PROPERTIES].pop(TemplateFields.ALARM_NAME)

        # Test action
        result = RaiseAlarmValidator.validate(action, idx)

        # Test assertions
        self._assert_fault_result(result, 125)

    @staticmethod
    def _create_raise_alarm_action(target):

        action_target = {
            TemplateFields.TARGET: target
        }
        properties = {
            TemplateFields.ALARM_NAME: 'VM_CPU_SUBOPTIMAL_PERFORMANCE',
            TemplateFields.SEVERITY: 'critical'
        }
        action = {
            TemplateFields.ACTION_TYPE: ActionType.RAISE_ALARM,
            TemplateFields.ACTION_TARGET: action_target,
            TemplateFields.PROPERTIES: properties
        }
        return action
