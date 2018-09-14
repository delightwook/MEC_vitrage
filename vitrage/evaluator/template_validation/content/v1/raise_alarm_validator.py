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

from vitrage.evaluator.template_fields import TemplateFields
from vitrage.evaluator.template_validation.content.base import \
    ActionValidator
from vitrage.evaluator.template_validation.content.base import \
    get_content_fault_result
from vitrage.evaluator.template_validation.content.base import \
    validate_template_id
from vitrage.evaluator.template_validation.status_messages import status_msgs


LOG = log.getLogger(__name__)


class RaiseAlarmValidator(ActionValidator):

    @staticmethod
    def validate(action, definitions_index):
        if TemplateFields.ACTION_TARGET not in action:
            LOG.error('%s status code: %s' % (status_msgs[124], 124))
            return get_content_fault_result(124)

        properties = action[TemplateFields.PROPERTIES]

        if TemplateFields.ALARM_NAME not in properties:
            LOG.error('%s status code: %s' % (status_msgs[125], 125))
            return get_content_fault_result(125)

        if TemplateFields.SEVERITY not in properties:
            LOG.error('%s status code: %s' % (status_msgs[126], 126))
            return get_content_fault_result(126)

        action_target = action[TemplateFields.ACTION_TARGET]
        if TemplateFields.TARGET not in action_target:
            LOG.error('%s status code: %s' % (status_msgs[127], 127))
            return get_content_fault_result(127)

        target = action_target[TemplateFields.TARGET]
        return validate_template_id(definitions_index, target)
