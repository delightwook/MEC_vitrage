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
from vitrage.entity_graph.mappings.handler_base import HandlerBase
from vitrage.entity_graph.mappings.operational_alarm_severity \
    import OperationalAlarmSeverity


class AlarmHandler(HandlerBase):

    def __init__(self):
        super(AlarmHandler, self).__init__()

    def undefined_property(self):
        return OperationalAlarmSeverity.NA

    def value_properties(self):
        return [VProps.SEVERITY]

    def set_operational_value(self, new_vertex, operational_value):
        new_vertex[VProps.VITRAGE_OPERATIONAL_SEVERITY] = operational_value

    def set_aggregated_value(self, new_vertex, aggregated_value):
        new_vertex[VProps.VITRAGE_AGGREGATED_SEVERITY] = aggregated_value

    def default_values(self):
        return [(None, OperationalAlarmSeverity.NA, 0)]

    def get_value_class_instance(self):
        return OperationalAlarmSeverity()
