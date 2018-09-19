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

from vitrage.datasources.zabbix.properties import ZabbixProperties \
    as ZabbixProps
from vitrage.tests import base


class ZabbixBaseTest(base.BaseTest):
    def _assert_contains(self, expected_serv, alarms):
        for alarm in alarms:
            if alarm[ZabbixProps.RESOURCE_NAME] == \
                expected_serv[ZabbixProps.RESOURCE_NAME] and \
                    alarm[ZabbixProps.TRIGGER_ID] == \
                    expected_serv[ZabbixProps.TRIGGER_ID]:
                self._assert_expected_alarm(expected_serv, alarm)
                return

        self.fail("alarm not found: %s %s" %
                  (expected_serv[ZabbixProps.RESOURCE_NAME],
                   expected_serv[ZabbixProps.TRIGGER_ID]))

    def _assert_expected_alarm(self, expected_alarm, alarm):
        for key, value in expected_alarm.items():
            self.assertEqual(value, alarm[key], 'wrong value for ' + key)
