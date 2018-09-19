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

from vitrage.evaluator.template_validation.status_messages import status_msgs
from vitrage.evaluator.template_validation import template_syntax_validator
from vitrage.tests import base
from vitrage.tests.mocks import utils
from vitrage.utils import file as file_utils


class DefTemplateSyntaxValidatorTest(base.BaseTest):

    # noinspection PyPep8Naming
    @classmethod
    def setUpClass(cls):
        super(DefTemplateSyntaxValidatorTest, cls).setUpClass()

        cls.def_template_dir_path = utils.get_resources_dir() + \
            '/templates/def_template_tests'

    def test_def_template_with_include_section(self):

        def_template_path = self.def_template_dir_path + \
            '/definition_templates/with_include.yaml'
        def_template = file_utils.load_yaml_file(def_template_path)
        self._test_execution_with_fault_result_for_def_template(def_template,
                                                                143)

    def test_def_template_with_scenario_section(self):

        def_template_path = self.def_template_dir_path + \
            '/definition_templates/with_scenarios.yaml'
        def_template = file_utils.load_yaml_file(def_template_path)
        self._test_execution_with_fault_result_for_def_template(def_template,
                                                                143)

    def test_basic_def_template(self):
        template_path = self.def_template_dir_path +\
            '/templates/basic_with_include.yaml'
        template = file_utils.load_yaml_file(template_path)

        self._test_execution_with_correct_result(template)

    def _test_execution_with_fault_result_for_def_template(self,
                                                           def_template,
                                                           expected_code):

        result = template_syntax_validator.def_template_syntax_validation(
            def_template)

        # Test assertions
        self.assertFalse(result.is_valid_config)
        self.assertTrue(result.comment.startswith(status_msgs[expected_code]))
        self.assertEqual(expected_code, result.status_code)

    def _test_execution_with_correct_result(self, template):

        # Test action
        result = template_syntax_validator.syntax_validation(template)

        # Test assertions
        self.assertTrue(result.is_valid_config)
        self.assertEqual(result.comment, status_msgs[0])
        self.assertEqual(0, result.status_code)
