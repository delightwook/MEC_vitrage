# Copyright 2018 - Nokia
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
import time

from oslo_log import log
import oslo_messaging

from vitrage import messaging
from vitrage import rpc as vitrage_rpc

LOG = log.getLogger(__name__)


def create_rpc_client_instance(conf):
    transport = messaging.get_rpc_transport(conf)
    target = oslo_messaging.Target(topic=conf.rpc_topic_collector)
    client = vitrage_rpc.get_client(transport, target)
    return client


def get_all(rpc_client, events_coordination, driver_names, action,
            retry_on_fault=False, first_call_timeout=None):
    LOG.info('get_all starting for %s', driver_names)
    t1 = time.time()

    def _call(_client):
        return _client.call(
            {},
            'driver_get_all',
            driver_names=driver_names,
            action=action,
            retry_on_fault=retry_on_fault)

    try:
        if first_call_timeout:
            # create a temporary client instance with a timeout
            client = rpc_client.prepare(timeout=first_call_timeout)
            events = _call(client)
        else:
            events = _call(rpc_client)
    except oslo_messaging.MessagingTimeout:
        LOG.exception('Got MessagingTimeout')
        events = _call(rpc_client) if retry_on_fault else []
    t2 = time.time()
    events_coordination.handle_multiple_low_priority(events)
    t3 = time.time()
    LOG.info('get_all took %s, processing took %s for %s events',
             t2 - t1, t3 - t2, len(events))


def get_changes(rpc_client, events_coordination, driver_name):
    LOG.info('get_changes starting %s', driver_name)
    events = rpc_client.call(
        {},
        'driver_get_changes',
        driver_name=driver_name)
    events_coordination.handle_multiple_low_priority(events)
