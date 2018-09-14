# Copyright 2016 - Nokia Corporation
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


import json
import pecan


from oslo_log import log
from oslo_utils.strutils import bool_from_string
from osprofiler import profiler
from pecan.core import abort

from vitrage.api.controllers.rest import RootRestController
from vitrage.api.controllers.v1 import count
from vitrage.api.policy import enforce
from vitrage.common.constants import TenantProps
from vitrage.common.constants import VertexProperties as Vprops


LOG = log.getLogger(__name__)


# noinspection PyBroadException
@profiler.trace_cls("alarm controller",
                    info={}, hide_args=False, trace_private=False)
class AlarmsController(RootRestController):
    count = count.CountsController()

    @pecan.expose('json')
    def get_all(self, **kwargs):
        vitrage_id = kwargs.get(Vprops.VITRAGE_ID)
        all_tenants = kwargs.get(TenantProps.ALL_TENANTS, False)
        all_tenants = bool_from_string(all_tenants)
        if all_tenants:
            enforce("list alarms:all_tenants", pecan.request.headers,
                    pecan.request.enforcer, {})
        else:
            enforce("list alarms", pecan.request.headers,
                    pecan.request.enforcer, {})

        LOG.info('returns list alarms with vitrage id %s', vitrage_id)

        try:
            return self._get_alarms(vitrage_id, all_tenants)
        except Exception:
            LOG.exception('Failed to get alarms.')
            abort(404, 'Failed to get alarms.')

    @staticmethod
    def _get_alarms(vitrage_id=None, all_tenants=False):
        alarms_json = pecan.request.client.call(pecan.request.context,
                                                'get_alarms',
                                                vitrage_id=vitrage_id,
                                                all_tenants=all_tenants)
        LOG.info(alarms_json)

        try:
            alarms_list = json.loads(alarms_json)['alarms']
            return alarms_list

        except Exception:
            LOG.exception('Failed to open file.')
            abort(404, 'Failed to get alarms')

    @pecan.expose('json')
    def get(self, vitrage_id):
        enforce("get alarm",
                pecan.request.headers,
                pecan.request.enforcer,
                {})

        LOG.info('returns show alarm with vitrage id %s', vitrage_id)

        try:
            return self._show_alarm(vitrage_id)
        except Exception:
            LOG.exception('Failed to load JSON.')
            abort(404, "Failed to show alarm.")

    @staticmethod
    def _show_alarm(vitrage_id):
        alarm_json = pecan.request.client.call(pecan.request.context,
                                               'show_alarm',
                                               vitrage_id=vitrage_id)
        LOG.info(alarm_json)

        try:
            alarms_list = json.loads(alarm_json)
            return alarms_list

        except Exception:
            LOG.exception('Failed to load JSON.')
            abort(404, 'Failed to show alarm.')
