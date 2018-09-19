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
from vitrage.common.constants import EdgeLabel
from vitrage.common.constants import EdgeProperties
from vitrage.evaluator.actions.recipes.action_steps import ADD_EDGE
from vitrage.evaluator.actions.recipes.action_steps import REMOVE_EDGE
from vitrage.evaluator.actions.recipes import base
from vitrage.evaluator.actions.recipes.base import ActionStepWrapper
from vitrage.evaluator.template_fields import TemplateFields as TFields


class AddCausalRelationship(base.Recipe):
    """Connect two alarms in the graph to indicate one cause other (RCA)

    The 'get_do_recipe' and 'get_undo_recipe' receive action_spec as input.
    The action_spec contains the following fields: type, targets and
    properties. example input:

    action_spec = ActionSpecs('type'= 'add_causal_relationship',
                              'targets'= {target: id, source: id},
                              'properties' = {}
    """

    @staticmethod
    def get_do_recipe(action_spec):

        edge_params = AddCausalRelationship._get_edge_params(
            action_spec.targets)
        add_edge_step = ActionStepWrapper(ADD_EDGE, edge_params)

        return [add_edge_step]

    @staticmethod
    def get_undo_recipe(action_spec):

        edge_params = AddCausalRelationship._get_edge_params(
            action_spec.targets)
        remove_edge_step = ActionStepWrapper(REMOVE_EDGE, edge_params)

        return [remove_edge_step]

    @staticmethod
    def _get_edge_params(params):

        return {
            TFields.SOURCE: params[TFields.SOURCE].vertex_id,
            TFields.TARGET: params[TFields.TARGET].vertex_id,
            EdgeProperties.RELATIONSHIP_TYPE: EdgeLabel.CAUSES
        }
