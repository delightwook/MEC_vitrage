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

from copy import deepcopy
from vitrage.evaluator.actions.recipes.execute_mistral import INPUT
from vitrage.evaluator.actions.recipes.execute_mistral import WORKFLOW
from vitrage.evaluator.template_fields import TemplateFields as TFields
from vitrage.evaluator.template_loading.v1.action_loader import \
    BaseActionLoader


class ExecuteMistralLoader(BaseActionLoader):
    def _get_properties(self, action_dict):
        """Place all properties under an 'input' block"""
        properties = action_dict.get(TFields.PROPERTIES, {})
        input_properties = deepcopy(properties)
        input_properties.pop(WORKFLOW)
        return {WORKFLOW: properties[WORKFLOW], INPUT: input_properties}
