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

from vitrage.datasources.nova.host import NOVA_HOST_DATASOURCE
from vitrage.datasources.nova.nova_driver_base import NovaDriverBase


class HostDriver(NovaDriverBase):

    def get_all(self, datasource_action):
        hosts = self.client.services.list(binary='nova-compute')
        return self.make_pickleable(
            [h.to_dict() for h in hosts],
            NOVA_HOST_DATASOURCE,
            datasource_action,
            *self.properties_to_filter_out())

    @staticmethod
    def properties_to_filter_out():
        return ['manager']
