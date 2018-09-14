# Copyright 2016 - Alcatel-Lucent
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,  software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND,  either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from vitrage.common.constants import DatasourceAction
from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.common.constants import GraphAction
from vitrage.datasources.nova.instance import NOVA_INSTANCE_DATASOURCE
from vitrage.datasources.nova.nova_driver_base import NovaDriverBase


class InstanceDriver(NovaDriverBase):

    @staticmethod
    def extract_events(instances):
        events = [instance.__dict__ for instance in instances]
        for e in events:
            if e['status'].lower() == 'deleted':
                e[DSProps.EVENT_TYPE] = GraphAction.DELETE_ENTITY
        return events

    def get_all(self, datasource_action):
        return self.make_pickleable(
            self.extract_events(self.client.servers.list(
                search_opts={'all_tenants': 1})),
            NOVA_INSTANCE_DATASOURCE,
            datasource_action,
            *self.properties_to_filter_out())

    def enrich_event(self, event, event_type):
        event[DSProps.EVENT_TYPE] = event_type

        return InstanceDriver.make_pickleable([event],
                                              NOVA_INSTANCE_DATASOURCE,
                                              DatasourceAction.UPDATE)[0]

    @staticmethod
    def properties_to_filter_out():
        return ['manager', 'OS-EXT-SRV-ATTR:user_data', '_info']

    @staticmethod
    def get_event_types():
        # Add event_types to receive notifications about
        return ['compute.instance.create.error',
                'compute.instance.create.end',
                'compute.instance.delete.start',
                'compute.instance.delete.end',
                'compute.instance.finish_resize.end',
                'compute.instance.live_migration.post.dest.end',
                'compute.instance.live_migration._post.end',
                'compute.instance.power_off.end',
                'compute.instance.power_on.end',
                'compute.instance.reboot.end',
                'compute.instance.rebuild.end',
                'compute.instance.resize.end',
                'compute.instance.resize.revert.end',
                'compute.instance.resume.end',
                'compute.instance.shutdown.end',
                'compute.instance.suspend.end',
                'compute.instance.volume.attach',
                'compute.instance.volume.detach',
                'compute.instance.pause.end',
                'compute.instance.unpause.end']
