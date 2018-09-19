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

from unittest import TestCase

from vitrage.datasources.collectd.mapper import CollectdMapper
from vitrage.datasources.collectd.properties \
    import CollectdProperties as CProps


class TestCollectdMapper(TestCase):
    def setUp(self):
        super(TestCollectdMapper, self).setUp()
        self.mapping = {
            'host1': {CProps.RESOURCE_TYPE: 'value_host1',
                      CProps.RESOURCE_NAME: 'value_host1'},
            'host_(.*)': {CProps.RESOURCE_TYPE: 'value_host_2',
                          CProps.RESOURCE_NAME: 'value_host_2'},
            'host-(.*)': {CProps.RESOURCE_TYPE: 'value_hostX',
                          CProps.RESOURCE_NAME: '${collectd_host}'},
            'hostabc': {CProps.RESOURCE_TYPE: 'type_host_abc',
                        CProps.RESOURCE_NAME: 'name_host_abc'}
        }

        self.mapper = CollectdMapper(self.mapping)

    def test_match_resource_no_regex(self):
        self.should_match('host1', 'host1')

    def test_match_resource_with_regex_concrete_value(self):
        self.should_match('host_1', 'host_(.*)')

    def test_match_resource_with_regex_parameter_value(self):
        self.should_match_on_collectd_host_param('host-5', 'host-(.*)')

    def test_no_match(self):
        self.should_not_match('host2')

    def test_match_ambiguous_value(self):
        # the host name is "hosta.c",
        # dot is part of the host name NOT a wildcard
        # should not match "hostabc"
        self.should_not_match('hosta.c')

    def should_match(self, host, expected):
        value = self.mapper.find(host)
        resource_name = value[CProps.RESOURCE_NAME]
        resource_type = value[CProps.RESOURCE_TYPE]
        expected_name = self.mapping[expected][CProps.RESOURCE_NAME]
        expected_type = self.mapping[expected][CProps.RESOURCE_TYPE]

        self.assertEqual(resource_name, expected_name)
        self.assertEqual(resource_type, expected_type)

    def should_match_on_collectd_host_param(self, host, expected):
        value = self.mapper.find(host)
        resource_name = value[CProps.RESOURCE_NAME]
        resource_type = value[CProps.RESOURCE_TYPE]
        expected_name = self.mapping[expected][CProps.RESOURCE_NAME]
        expected_type = self.mapping[expected][CProps.RESOURCE_TYPE]

        self.assertEqual('${collectd_host}', expected_name)
        self.assertEqual(resource_name, host)
        self.assertEqual(resource_type, expected_type)

    def should_not_match(self, host):
        self.assertRaises(KeyError, self.mapper.find, host)
