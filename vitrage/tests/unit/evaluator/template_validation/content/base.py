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

import logging

from vitrage.common.constants import EntityCategory
from vitrage.evaluator.template_fields import TemplateFields
from vitrage.evaluator.template_validation.status_messages import status_msgs
from vitrage.tests import base


DEFINITIONS_INDEX_MOCK = {
    '123': {},
    '456': {},
    '789': {},
    'a1': {
        TemplateFields.CATEGORY: EntityCategory.ALARM
    },
    'a2': {
        TemplateFields.CATEGORY: EntityCategory.ALARM
    }
}


class ValidatorTest(base.BaseTest):

    def _assert_correct_result(self, result):

        self.assertTrue(result.is_valid_config)
        self.assertEqual(result.comment, status_msgs[0])
        self.assertEqual(0, result.status_code)

    def _assert_fault_result(self, result, status_code):

        self.assertFalse(result.is_valid_config)
        self.assertTrue(result.comment.startswith(status_msgs[status_code]))
        self.assertEqual(result.status_code, status_code)

    def _assert_warning_result(self, result, status_code):

        self.assertTrue(result.is_valid_config)
        self.assertTrue(result.comment.startswith(status_msgs[status_code]))
        self.assertEqual(result.status_code, status_code)

    @staticmethod
    def _hide_useless_logging_messages():

        validator_path = 'vitrage.evaluator.template_validation.' \
                         'template_content_validator'
        content_validator_log = logging.getLogger(validator_path)
        content_validator_log.setLevel(logging.FATAL)


class ActionValidatorTest(ValidatorTest):

    # noinspection PyPep8Naming
    @classmethod
    def setUpClass(cls):
        super(ActionValidatorTest, cls).setUpClass()

        cls._hide_useless_logging_messages()

    def _validate_action(self, action, validation_func):

        # Test setup
        idx = DEFINITIONS_INDEX_MOCK.copy()

        # Test action and assertions
        result = validation_func(action, idx)

        # Test Assertions
        self._assert_correct_result(result)

    def _validate_action_without_action_target(self, action, validation_func):

        # Test setup
        idx = DEFINITIONS_INDEX_MOCK.copy()
        action.pop(TemplateFields.ACTION_TARGET)

        # Test action
        result = validation_func(action, idx)

        # Test assertions
        self._assert_fault_result(result, 124)

    def _validate_action_with_invalid_target_id(self, action, validation_func):

        # Test setup
        idx = DEFINITIONS_INDEX_MOCK.copy()

        # Test action
        result = validation_func(action, idx)

        # Test assertions
        self._assert_fault_result(result, 3)

    def _validate_action_without_target_id(self,
                                           action,
                                           validation_func,
                                           expected_status_code):

        # Test setup
        idx = DEFINITIONS_INDEX_MOCK.copy()
        action[TemplateFields.ACTION_TARGET].pop(TemplateFields.TARGET)

        # Test action
        result = validation_func(action, idx)

        # Test assertions
        self._assert_fault_result(result, expected_status_code)
