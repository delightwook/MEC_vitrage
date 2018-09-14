# Copyright 2018 - Nokia
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

from oslo_config import cfg
from testtools import matchers

from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.datasources.prometheus.driver import PROMETHEUS_EVENT_TYPE
from vitrage.datasources.prometheus.driver import PrometheusDriver
from vitrage.datasources.prometheus import PROMETHEUS_DATASOURCE
from vitrage.tests import base
from vitrage.tests.mocks import mock_driver


# noinspection PyProtectedMember
class PrometheusDriverTest(base.BaseTest):
    OPTS = []

    # noinspection PyPep8Naming
    @classmethod
    def setUpClass(cls):
        cls.conf = cfg.ConfigOpts()
        cls.conf.register_opts(cls.OPTS, group=PROMETHEUS_DATASOURCE)

    def test_enrich_event(self):
        # Test setup
        driver = PrometheusDriver(self.conf)
        event = self._generate_event()

        # Enrich event
        created_events = driver.enrich_event(event, PROMETHEUS_EVENT_TYPE)

        # Test assertions
        self._assert_event_equal(created_events, PROMETHEUS_EVENT_TYPE)

    @staticmethod
    def _generate_event():
        generators = mock_driver.simple_prometheus_alarm_generators(
            update_vals={})

        return mock_driver.generate_sequential_events_list(generators)[0]

    def _assert_event_equal(self,
                            created_events,
                            expected_event_type):
        self.assertIsNotNone(created_events, 'No events returned')
        self.assertThat(created_events, matchers.HasLength(1),
                        'Expected one event')
        self.assertEqual(expected_event_type,
                         created_events[0][DSProps.EVENT_TYPE])
