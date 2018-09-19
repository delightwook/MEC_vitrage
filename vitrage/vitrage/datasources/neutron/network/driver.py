# Copyright 2016 - Alcatel-Lucent
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,  software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND,  either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from vitrage.common.constants import DatasourceAction
from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.datasources.neutron.base import NeutronBase
from vitrage.datasources.neutron.network import NEUTRON_NETWORK_DATASOURCE


# noinspection PyAbstractClass
class NetworkDriver(NeutronBase):

    @staticmethod
    def get_event_types():
        return ['network.create.end',
                'network.update.end',
                'network.delete.end']

    def enrich_event(self, event, event_type):
        event[DSProps.EVENT_TYPE] = event_type

        return NetworkDriver.make_pickleable([event],
                                             NEUTRON_NETWORK_DATASOURCE,
                                             DatasourceAction.UPDATE)[0]

    @staticmethod
    def properties_to_filter_out():
        """Return a list of properties to be removed from the event"""
        return ['manager', '_info']

    def get_all(self, datasource_action):
        return self.make_pickleable(
            self.client.list_networks()['networks'],
            NEUTRON_NETWORK_DATASOURCE,
            datasource_action)
