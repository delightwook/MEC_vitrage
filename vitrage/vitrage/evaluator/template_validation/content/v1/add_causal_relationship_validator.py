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

from oslo_log import log

from vitrage.common.constants import EntityCategory
from vitrage.evaluator.template_fields import TemplateFields
from vitrage.evaluator.template_validation.content.base import \
    ActionValidator
from vitrage.evaluator.template_validation.content.base import \
    get_content_correct_result
from vitrage.evaluator.template_validation.content.base import \
    get_content_fault_result
from vitrage.evaluator.template_validation.content.base import \
    validate_template_id
from vitrage.evaluator.template_validation.status_messages import status_msgs


LOG = log.getLogger(__name__)


class AddCausalRelationshipValidator(ActionValidator):

    @staticmethod
    def validate(action, definitions_index):
        if TemplateFields.ACTION_TARGET not in action:
            LOG.error('%s status code: %s' % (status_msgs[124], 124))
            return get_content_fault_result(124)

        action_target = action[TemplateFields.ACTION_TARGET]

        for key in [TemplateFields.TARGET, TemplateFields.SOURCE]:
            if key not in action_target:
                LOG.error('%s status code: %s' % (status_msgs[130], 130))
                return get_content_fault_result(130)

            template_id = action_target[key]
            result = validate_template_id(definitions_index, template_id)

            if not result.is_valid_config:
                return result

            entity = definitions_index[template_id]
            result = AddCausalRelationshipValidator._validate_entity_category(
                entity,
                EntityCategory.ALARM)
            if not result.is_valid_config:
                return result

        return get_content_correct_result()

    @staticmethod
    def _validate_entity_category(entity_to_check, category):

        if TemplateFields.CATEGORY not in entity_to_check \
                or entity_to_check[TemplateFields.CATEGORY] != category:
            msg = status_msgs[132] + ' expect %s to be %s' \
                                     % (entity_to_check, category)
            LOG.error('%s status code: %s' % (msg, 132))
            return get_content_fault_result(132, msg)

        return get_content_correct_result()
