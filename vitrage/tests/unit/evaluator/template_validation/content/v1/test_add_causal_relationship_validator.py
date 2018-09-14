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
from vitrage.evaluator.template_validation.content.v1.\
    add_causal_relationship_validator import AddCausalRelationshipValidator
from vitrage.tests.unit.evaluator.template_validation.content.base import \
    ActionValidatorTest
from vitrage.tests.unit.evaluator.template_validation.content.base import \
    DEFINITIONS_INDEX_MOCK


class AddCausalRelationshipValidatorTest(ActionValidatorTest):

    def test_validate_add_causal_relationship_action(self):

        self._validate_action(
            self._create_add_causal_relationship_action('a1', 'a2'),
            AddCausalRelationshipValidator.validate
        )

    def test_validate_add_causal_relation_action_without_action_target(self):

        self._validate_action_without_action_target(
            self._create_add_causal_relationship_action('a1', 'a2'),
            AddCausalRelationshipValidator.validate
        )

    def test_validate_add_causal_relationship_action_with_invalid_target(self):

        self._validate_action_with_invalid_target_id(
            self._create_add_causal_relationship_action('unknown', 'a2'),
            AddCausalRelationshipValidator.validate
        )

    def test_validate_add_causal_relationship_action_with_invalid_source(self):

        self._validate_action_with_invalid_target_id(
            self._create_add_causal_relationship_action('a1', 'unknown'),
            AddCausalRelationshipValidator.validate
        )

    def test_validate_add_causal_relationship_action_without_target(self):

        self._validate_action_without_target_id(
            self._create_add_causal_relationship_action('a1', 'a2'),
            AddCausalRelationshipValidator.validate,
            130
        )

    def test_validate_add_causal_relationship_action_without_source(self):

        # Test setup
        idx = DEFINITIONS_INDEX_MOCK.copy()
        action = self._create_add_causal_relationship_action('a1', 'a2')
        action[TemplateFields.ACTION_TARGET].pop(TemplateFields.SOURCE, None)

        # Test action
        result = AddCausalRelationshipValidator.validate(action, idx)

        # Test assertion
        self._assert_fault_result(result, 130)

    def test_validate_add_causal_relationship_action_wrong_src_category(self):

        # Test setup
        idx = DEFINITIONS_INDEX_MOCK.copy()
        action = self._create_add_causal_relationship_action('a1', '123')

        # Test action
        result = AddCausalRelationshipValidator.validate(action, idx)

        # Test assertion
        self._assert_fault_result(result, 132)

    def test_validate_add_causal_relationship_action_wrong_tgt_category(self):

        # Test setup
        idx = DEFINITIONS_INDEX_MOCK.copy()
        action = self._create_add_causal_relationship_action('123', 'a1')

        # Test action
        result = AddCausalRelationshipValidator.validate(action, idx)

        # Test assertion
        self._assert_fault_result(result, 132)

    @staticmethod
    def _create_add_causal_relationship_action(target, source):

        action_target = {
            TemplateFields.TARGET: target,
            TemplateFields.SOURCE: source
        }
        action = {
            TemplateFields.ACTION_TYPE: ActionType.ADD_CAUSAL_RELATIONSHIP,
            TemplateFields.ACTION_TARGET: action_target}

        return action
