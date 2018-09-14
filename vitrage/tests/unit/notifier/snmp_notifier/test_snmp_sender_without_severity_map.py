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

from oslo_config import cfg
from testtools import matchers

from vitrage.common.constants import VertexProperties as VProps
import vitrage.notifier.plugins.snmp.snmp_sender as sender
from vitrage.notifier.plugins.snmp.snmp_sender import SnmpSender
from vitrage.tests import base
from vitrage.tests.mocks import utils
from vitrage.tests.unit.notifier.snmp_notifier import common


class SnmpNotifierTest(base.BaseTest):
    simple_opts = [
        cfg.StrOpt('notifier',
                   default='vitrage.notifier.plugins.snmp.'
                           'snmp_notifier.SnmpNotifier',
                   required=True),
        cfg.StrOpt('snmp_sender_class',
                   default='vitrage.notifier.plugins.snmp.'
                           'snmp_sender.SnmpSender',
                   required=True),
        cfg.StrOpt('alarm_oid_mapping',
                   default=utils.get_resources_dir() +
                   '/snmp_notifier/alarm_oid_mapping.yaml'),
        cfg.StrOpt('consumers',
                   default=utils.get_resources_dir() +
                   '/snmp_notifier/dests.yaml'),
        cfg.StrOpt('oid_tree',
                   default=utils.get_resources_dir() +
                   '/snmp_notifier/'
                   'oid_tree_without_severity_mapping.yaml'),
    ]

    # noinspection PyPep8Naming
    @classmethod
    def setUpClass(cls):
        super(SnmpNotifierTest, cls).setUpClass()

        cls.conf = cfg.ConfigOpts()
        cls.conf.register_opts(cls.simple_opts, group='snmp')
        cls.snmp_sender = SnmpSender(cls.conf)

    def test_create_oids(self):

        oids, var_lst = self.snmp_sender._build_oids()

        self.assertThat(oids, matchers.HasLength(4))
        self.assertThat(var_lst, matchers.HasLength(3))

        self.assertIn(VProps.NAME, oids)
        self.assertIn(VProps.VITRAGE_IS_DELETED, oids)
        self.assertIn(VProps.VITRAGE_OPERATIONAL_SEVERITY, oids)
        self.assertIn(sender.ALARM_OID, oids)

        self.assertIn(VProps.NAME, var_lst)
        self.assertIn(VProps.VITRAGE_IS_DELETED, var_lst)
        self.assertIn(VProps.VITRAGE_OPERATIONAL_SEVERITY, var_lst)

    def test_get_severity_oid(self):

        alert_severity_oid = \
            self.snmp_sender._get_severity_oid(common.alarm_data)

        self.assertIsNone(alert_severity_oid)

    def test_get_alert_oid(self):

        alert_severity_oid = \
            self.snmp_sender._get_severity_oid(common.alarm_data)
        alert_details = self.snmp_sender.alarm_mapping.get(common.name_)

        self.assertEqual(alert_details.get(sender.OID), common.ALERT_OID)

        alert_oid = self.snmp_sender._get_alert_oid(alert_details[sender.OID],
                                                    alert_severity_oid)

        self.assertEqual(alert_oid, common.GENERAL_OID + '.' +
                         common.COMPANY_OID + '.' + common.ALARM_PREFIX_OID +
                         common.ALERT_OID)

    def test_get_details(self):
        alert_details, alert_severity_oid = \
            self.snmp_sender._get_details(common.alarm_data)

        self.assertEqual(alert_details, common.alert_details)
        self.assertIsNone(alert_severity_oid)
