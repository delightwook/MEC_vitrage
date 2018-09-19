# Copyright 2017 - Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from vitrage.entity_graph.mappings.operational_alarm_severity import \
    OperationalAlarmSeverity

from vitrage.common.constants import EntityCategory
from vitrage.common.constants import VertexProperties as VProps


false_ = 'False'
name_ = 'VM network problem'

GENERAL_OID = '1.3.6.1.4.1'
COMPANY_OID = '1.1.1'
ALARM_OBJECTS_OID = '1'
ALARM_PREFIX_OID = '2'
NAME_OID = '1'
IS_DELETED_OID = '2'
SEVERITY_OID = '3'

ALERT_OID = '.100000'

alarm_data = {VProps.VITRAGE_CATEGORY: EntityCategory.ALARM,
              VProps.NAME: name_,
              VProps.RESOURCE + '_' + VProps.VITRAGE_IS_DELETED: false_,
              VProps.RESOURCE + '_' + VProps.VITRAGE_IS_PLACEHOLDER: false_,
              VProps.VITRAGE_IS_DELETED: false_,
              VProps.VITRAGE_OPERATIONAL_SEVERITY:
                  OperationalAlarmSeverity.CRITICAL,
              VProps.RESOURCE:
                  {VProps.VITRAGE_IS_PLACEHOLDER: false_,
                   VProps.VITRAGE_IS_DELETED: false_}}

alert_details = {'oid': ALERT_OID, 'alarm_name': 'vitrageDeducedTest'}
