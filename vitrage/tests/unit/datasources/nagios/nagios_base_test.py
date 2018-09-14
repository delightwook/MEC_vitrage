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

from vitrage.datasources.nagios.properties import NagiosProperties \
    as NagiosProps
from vitrage.tests import base


class NagiosBaseTest(base.BaseTest):
    def _assert_contains(self, expected_service, services):
        for service in services:
            if service[NagiosProps.RESOURCE_NAME] == \
                    expected_service[NagiosProps.RESOURCE_NAME] and \
                    service[NagiosProps.SERVICE] == \
                    expected_service[NagiosProps.SERVICE]:
                self._assert_expected_service(expected_service, service)
                return

        self.fail("service not found: %(resource_name)s %(service_name)s" %
                  {'resource_name':
                   expected_service[NagiosProps.RESOURCE_NAME],
                   'service_name':
                   expected_service[NagiosProps.SERVICE]})

    def _assert_expected_service(self, expected_service, service):
        for key, value in expected_service.items():
            self.assertEqual(value, service[key], 'wrong value for ' + key)
