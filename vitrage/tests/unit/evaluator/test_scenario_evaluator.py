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
from vitrage.evaluator.actions.base import ActionType
from vitrage.evaluator.scenario_evaluator import ScenarioEvaluator
from vitrage.evaluator.template_data import ActionSpecs
from vitrage.tests import base


class TestScenarioEvaluator(base.BaseTest):

    def test_verify_execute_mistral_v2_action_hash(self):
        execute_mistral_action_spec_1 = \
            ActionSpecs(id='mistmistmist1',
                        type=ActionType.EXECUTE_MISTRAL,
                        targets={},
                        properties={'workflow': 'wf4',
                                    'input': {
                                        'prop1': 'ppp',
                                        'prop2': 'qqq',
                                        'prop3': 'rrr',
                                    }})

        execute_mistral_action_spec_2 = \
            ActionSpecs(id='mistmistmist2',
                        type=ActionType.EXECUTE_MISTRAL,
                        targets={},
                        properties={'workflow': 'wf4',
                                    'input': {
                                        'prop2': 'qqq',
                                        'prop3': 'rrr',
                                        'prop1': 'ppp',
                                    }})

        self.assertEqual(ScenarioEvaluator.
                         _generate_action_id(execute_mistral_action_spec_1),
                         ScenarioEvaluator.
                         _generate_action_id(execute_mistral_action_spec_2))
