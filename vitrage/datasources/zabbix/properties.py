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


class ZabbixProperties(object):
    RESOURCE_TYPE = 'resource_type'
    RESOURCE_NAME = 'resource_name'
    DESCRIPTION = 'description'
    STATUS = 'status'
    ZABBIX_VALUE = 'zabbix_value'
    VALUE = 'value'
    HOST = 'host'
    HOST_ID = 'hostid'
    PRIORITY = 'priority'
    LAST_CHANGE = 'lastchange'
    TIMESTAMP = 'timestamp'
    ZABBIX_TIMESTAMP_FORMAT = '%Y.%m.%d %H:%M:%S'
    RAWTEXT = 'rawtext'
    TRIGGER_ID = 'triggerid'
    ZABBIX_RESOURCE_NAME = 'zabbix_resource_name'


class ZabbixTriggerValue(object):
    OK = '0'
    PROBLEM = '1'


class ZabbixTriggerStatus(object):
    ENABLED = '0'
    DISABLED = '1'


class ZabbixTriggerSeverity(object):

    INFORMATION = 'INFORMATION'
    WARNING = 'WARNING'
    AVERAGE = 'AVERAGE'
    HIGH = 'HIGH'
    DISASTER = 'DISASTER'
    NOT_CLASSIFIED = 'NOT CLASSIFIED'

    _SEVERITY_MAPPING = {
        '0': NOT_CLASSIFIED,
        '1': INFORMATION,
        '2': WARNING,
        '3': AVERAGE,
        '4': HIGH,
        '5': DISASTER
    }

    @staticmethod
    def str(num):
        return ZabbixTriggerSeverity._SEVERITY_MAPPING[num]
