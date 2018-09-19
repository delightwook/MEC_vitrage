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
from vitrage.api.policy import enforce


LOG = log.getLogger(__name__)


# noinspection PyBroadException
@profiler.trace_cls("rca controller",
                    info={}, hide_args=False, trace_private=False)
class RCAController(RootRestController):
    @pecan.expose('json')
    def index(self, alarm_id, all_tenants=False):
        return self.get(alarm_id, all_tenants)

    @pecan.expose('json')
    def get(self, alarm_id, all_tenants=False):
        all_tenants = bool_from_string(all_tenants)
        if all_tenants:
            enforce('get rca:all_tenants', pecan.request.headers,
                    pecan.request.enforcer, {})
        else:
            enforce('get rca', pecan.request.headers,
                    pecan.request.enforcer, {})

        LOG.info('received show rca with alarm id %s', alarm_id)
        return self.get_rca(alarm_id, all_tenants)

    @staticmethod
    def get_rca(alarm_id, all_tenants):
        try:
            graph_data = pecan.request.client.call(pecan.request.context,
                                                   'get_rca',
                                                   root=alarm_id,
                                                   all_tenants=all_tenants)
            LOG.info(graph_data)
            graph = json.loads(graph_data)
            return graph

        except Exception:
            LOG.exception('Failed to get RCA.')
            abort(404, 'Failed to get RCA')
