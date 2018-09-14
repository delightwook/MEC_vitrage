# Copyright 2015 - Alcatel-Lucent
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

from vitrage.datasources.nagios import NAGIOS_DATASOURCE
from vitrage.datasources.nagios.transformer import NagiosTransformer
from vitrage.datasources.nova.host import NOVA_HOST_DATASOURCE
from vitrage.datasources.nova.host.transformer import HostTransformer
from vitrage.datasources.nova.instance import NOVA_INSTANCE_DATASOURCE
from vitrage.datasources.nova.instance.transformer import InstanceTransformer
from vitrage.datasources.nova.zone import NOVA_ZONE_DATASOURCE
from vitrage.datasources.nova.zone.transformer import ZoneTransformer
from vitrage.entity_graph.processor.transformer_manager import\
    TransformerManager
from vitrage.opts import register_opts
from vitrage.tests import base


class TransformerManagerTest(base.BaseTest):

    OPTS = [
        cfg.ListOpt('types',
                    default=[NAGIOS_DATASOURCE,
                             NOVA_HOST_DATASOURCE,
                             NOVA_INSTANCE_DATASOURCE,
                             NOVA_ZONE_DATASOURCE],
                    help='Names of supported data sources'),

        cfg.ListOpt('path',
                    default=['vitrage.datasources'],
                    help='base path for data sources')
    ]

    # noinspection PyPep8Naming
    @classmethod
    def setUpClass(cls):
        super(TransformerManagerTest, cls).setUpClass()
        cls.conf = cfg.ConfigOpts()
        cls.conf.register_opts(cls.OPTS, group='datasources')

        for datasource in cls.conf.datasources.types:
            register_opts(cls.conf, datasource, cls.conf.datasources.path)

        cls.manager = TransformerManager(cls.conf)

    def test_transformer_registration_nagios(self):
            self.assertIsInstance(self.manager.get_transformer
                                  (NAGIOS_DATASOURCE), NagiosTransformer)

    def test_transformer_registration_nova_host(self):
        self.assertIsInstance(self.manager.get_transformer
                              (NOVA_HOST_DATASOURCE), HostTransformer)

    def test_transformer_registration_nova_instance(self):
        self.assertIsInstance(self.manager.get_transformer
                              (NOVA_INSTANCE_DATASOURCE), InstanceTransformer)

    def test_transformer_registration_nova_zone(self):
        self.assertIsInstance(self.manager.get_transformer
                              (NOVA_ZONE_DATASOURCE), ZoneTransformer)
