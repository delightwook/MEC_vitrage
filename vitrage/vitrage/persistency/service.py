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

from __future__ import print_function

import cotyledon
import dateutil.parser
import oslo_messaging as oslo_m

from oslo_log import log
from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.common.constants import GraphAction
from vitrage import messaging
from vitrage.storage.sqlalchemy import models


LOG = log.getLogger(__name__)


class PersistorService(cotyledon.Service):
    def __init__(self, worker_id, conf, db_connection):
        super(PersistorService, self).__init__(worker_id)
        self.conf = conf
        self.db_connection = db_connection
        transport = messaging.get_transport(conf)
        target = \
            oslo_m.Target(topic=conf.persistency.persistor_topic)
        self.listener = messaging.get_notification_listener(
            transport, [target],
            [VitragePersistorEndpoint(self.db_connection)])

    def run(self):
        LOG.info("Vitrage Persistor Service - Starting...")

        self.listener.start()

        LOG.info("Vitrage Persistor Service - Started!")

    def terminate(self):
        LOG.info("Vitrage Persistor Service - Stopping...")

        self.listener.stop()
        self.listener.wait()

        LOG.info("Vitrage Persistor Service - Stopped!")


class VitragePersistorEndpoint(object):
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        LOG.debug('Vitrage Event Info: payload %s', payload)
        self.process_event(payload)

    def process_event(self, data):
        """:param data: Serialized to a JSON formatted ``str`` """
        if data.get(DSProps.EVENT_TYPE) == GraphAction.END_MESSAGE:
            return
        collector_timestamp = \
            dateutil.parser.parse(data.get(DSProps.SAMPLE_DATE))
        event_row = models.Event(payload=data,
                                 collector_timestamp=collector_timestamp)
        self.db_connection.events.create(event_row)
