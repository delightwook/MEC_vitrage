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
from vitrage.common.constants import VertexProperties as VProps
from vitrage.evaluator.actions.recipes.action_steps import UPDATE_VERTEX
from vitrage.evaluator.actions.recipes import base
from vitrage.evaluator.actions.recipes.base import ActionStepWrapper
from vitrage.evaluator.template_fields import TemplateFields as TFields


class MarkDown(base.Recipe):
    """Mark A host as down.

    The 'get_do_recipe' and 'get_undo_recipe' receive action_spec as input.
    The action_spec contains the following fields: type, targets and
    properties. example input:

    action_spec = ActionSpecs('type'= {'set_state'},
                              'targets'= {target: Vertex},
                              'properties' = {is_marked_down : True}
    """

    @staticmethod
    def get_do_recipe(action_spec):

        update_vertex_step = MarkDown._get_update_vertex_step(
            action_spec.targets[TFields.TARGET].vertex_id,
            True)

        return [update_vertex_step]

    @staticmethod
    def get_undo_recipe(action_spec):

        update_vertex_step = MarkDown._get_update_vertex_step(
            action_spec.targets[TFields.TARGET].vertex_id,
            False)

        return [update_vertex_step]

    @staticmethod
    def _get_update_vertex_step(target_id, is_marked_down):

        update_vertex_params = {
            VProps.VITRAGE_ID: target_id,
            VProps.IS_REAL_VITRAGE_ID: True,
            VProps.IS_MARKED_DOWN: is_marked_down
        }
        update_vertex_step = ActionStepWrapper(UPDATE_VERTEX,
                                               update_vertex_params)

        return update_vertex_step
