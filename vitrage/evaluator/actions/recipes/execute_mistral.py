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
from vitrage.evaluator.actions.recipes.action_steps import EXECUTE_EXTERNAL
from vitrage.evaluator.actions.recipes.action_steps import EXECUTION_ENGINE
from vitrage.evaluator.actions.recipes import base
from vitrage.evaluator.actions.recipes.base import ActionStepWrapper


MISTRAL = 'mistral'
INPUT = 'input'
WORKFLOW = 'workflow'


class ExecuteMistral(base.Recipe):
    """Execute a Mistral workflow

    The 'get_do_recipe' and 'get_undo_recipe' receive action_spec as input.
    The action_spec contains the following fields: type and properties.

    example input:

    action_spec = ActionSpecs('type'= {'execute_mistral'},
                              'properties' = {workflow : wf_1,
                                              host: host_2,
                                              host_status: down}
    """

    @staticmethod
    def get_do_recipe(action_spec):

        execute_external_step = ExecuteMistral._get_execute_external_step(
            action_spec.properties
        )

        return [execute_external_step]

    @staticmethod
    def get_undo_recipe(action_spec):
        # No undo for execute an external action
        return []

    @staticmethod
    def _get_execute_external_step(properties):

        properties[EXECUTION_ENGINE] = MISTRAL
        execute_external_step = ActionStepWrapper(EXECUTE_EXTERNAL,
                                                  properties)

        return execute_external_step
