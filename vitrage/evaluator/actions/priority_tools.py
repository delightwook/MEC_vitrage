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
from vitrage.entity_graph.mappings.datasource_info_mapper \
    import DEFAULT_INFO_MAPPER
from vitrage.evaluator.template_fields import TemplateFields


class BaselineTools(object):
    @staticmethod
    def get_score(action_info):
        return 1  # no priorities

    @classmethod
    def get_extra_info(cls, action_specs):
        return None


class RaiseAlarmTools(object):

    def __init__(self, scores):
        self.scores = scores

    def get_score(self, action_info):
        severity = action_info.specs.properties[TemplateFields.SEVERITY]
        return self.scores.get(severity.upper(), 0)

    @classmethod
    def get_extra_info(cls, action_specs):
        return action_specs.properties[TemplateFields.ALARM_NAME]


class SetStateTools(object):

    def __init__(self, scores):
        self.scores = scores

    def get_score(self, action_info):
        state = action_info.specs.properties[TemplateFields.STATE].upper()
        target_resource = action_info.specs.targets[TemplateFields.TARGET]
        target_vitrage_type = target_resource[VProps.VITRAGE_TYPE]
        score_name = target_vitrage_type \
            if target_vitrage_type in self.scores else DEFAULT_INFO_MAPPER
        return self.scores[score_name].get(state, 0)

    @classmethod
    def get_extra_info(cls, action_specs):
        return None
