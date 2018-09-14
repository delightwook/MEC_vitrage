# Copyright 2018 - Nokia, ZTE
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR  CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_config import cfg
from vitrage.common.constants import DatasourceOpts as DSOpts
from vitrage.common.constants import UpdateMethod

MOCK_DATASOURCE = 'mock_graph_datasource'

OPTS = [
    cfg.StrOpt(DSOpts.TRANSFORMER,
               default='vitrage.tests.mocks.mock_graph_datasource.transformer'
                       '.MockTransformer',
               help='Mock transformer class path',
               required=True),
    cfg.StrOpt(DSOpts.DRIVER,
               default='vitrage.tests.mocks.mock_graph_datasource.driver.'
                       'MockDriver',
               help='Mock driver class path',
               required=True),
    cfg.StrOpt(DSOpts.UPDATE_METHOD,
               default=UpdateMethod.NONE,
               help='None: updates only via Vitrage periodic snapshots.'
                    'Pull: updates periodically.'
                    'Push: updates by getting notifications from the'
                    ' datasource itself.',
               required=True),
    cfg.IntOpt('networks', default=3),
    cfg.IntOpt('zones_per_cluster', default=2),
    cfg.IntOpt('hosts_per_zone', default=2),
    cfg.IntOpt('zabbix_alarms_per_host', default=2),
    cfg.IntOpt('instances_per_host', default=2),
    cfg.IntOpt('ports_per_instance', default=2),
    cfg.IntOpt('volumes_per_instance', default=2),
    cfg.IntOpt('vitrage_alarms_per_instance', default=0),
    cfg.IntOpt('tripleo_controllers', default=3),
    cfg.IntOpt('zabbix_alarms_per_controller', default=1),
]
