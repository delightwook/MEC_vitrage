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

from oslo_config import cfg

from vitrage.datasources.cinder.volume import CINDER_VOLUME_DATASOURCE
from vitrage.datasources.neutron.network import NEUTRON_NETWORK_DATASOURCE
from vitrage.datasources.neutron.port import NEUTRON_PORT_DATASOURCE
from vitrage.datasources.nova.host import NOVA_HOST_DATASOURCE
from vitrage.datasources.nova.instance import NOVA_INSTANCE_DATASOURCE
from vitrage.datasources.nova.zone import NOVA_ZONE_DATASOURCE

OPENSTACK_CLUSTER = 'openstack.cluster'

# Register options for the service
OPTS = [
    cfg.ListOpt('types',
                default=[NOVA_HOST_DATASOURCE,
                         NOVA_INSTANCE_DATASOURCE,
                         NOVA_ZONE_DATASOURCE,
                         CINDER_VOLUME_DATASOURCE,
                         NEUTRON_PORT_DATASOURCE,
                         NEUTRON_NETWORK_DATASOURCE,
                         ],
                help='Names of supported data sources'),
    cfg.ListOpt('path',
                default=['vitrage.datasources'],
                help='base path for data sources'),
    cfg.IntOpt('snapshots_interval',
               default=600,
               min=10,
               help='Time to wait between subsequent datasource snapshots'),
    cfg.IntOpt('snapshot_interval_on_fault',
               default=20,
               min=1,
               help='Time to wait until retrying to snapshot the datasource'
                    ' in case of fault'),
    cfg.ListOpt('notification_topics',
                default=['vitrage_notifications'],
                help='Vitrage configured notifications topic',
                deprecated_name='notification_topic'),
    cfg.StrOpt('notification_exchange',
               required=False,
               help='Exchange that is used for notifications.'),
    cfg.StrOpt('notification_topic_collector',
               default='vitrage_collector_notifications',
               help='The topic on which event will be sent from the '
                    'datasources to the graph processor')
]
