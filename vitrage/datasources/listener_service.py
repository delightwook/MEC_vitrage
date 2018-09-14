# Copyright 2016 - Nokia
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

from collections import defaultdict

from oslo_log import log
import oslo_messaging

from vitrage.datasources import utils
from vitrage import messaging
from vitrage.messaging import VitrageNotifier

LOG = log.getLogger(__name__)


class ListenerService(object):

    def __init__(self, conf):
        super(ListenerService, self).__init__()
        self.enrich_callbacks_by_events = \
            self._create_callbacks_by_events_dict(conf)

        topics = [conf.datasources.notification_topic_collector]
        if conf.persistency.enable_persistency:
            topics.append(conf.persistency.persistor_topic)
        else:
            LOG.warning("Not persisting events")
        notifier = VitrageNotifier(conf, 'driver.events', topics)
        self.listener = self._get_topics_listener(conf, notifier.notify)

    def start(self):
        LOG.info("Vitrage data source Listener Service - Starting...")

        self.listener.start()

        LOG.info("Vitrage data source Listener Service - Started!")

    def stop(self):
        LOG.info("Vitrage data source Listener Service - Stopping...")

        # Should it be here?
        # self.listener.stop()
        # self.listener.wait()

        LOG.info("Vitrage data source Listener Service - Stopped!")

    @classmethod
    def _create_callbacks_by_events_dict(cls, conf):
        ret = defaultdict(list)
        driver_names = utils.get_push_drivers_names(conf)
        push_drivers = utils.get_drivers_by_name(conf, driver_names)

        for driver in push_drivers:
            for event in driver.get_event_types():
                ret[event].append(driver.enrich_event)

        return ret

    def _get_topics_listener(self, conf, callback):
        topics = conf.datasources.notification_topics
        exchange = conf.datasources.notification_exchange
        transport = messaging.get_transport(conf)
        targets = [oslo_messaging.Target(exchange=exchange, topic=topic)
                   for topic in topics]

        return messaging.get_notification_listener(
            transport,
            targets,
            [NotificationsEndpoint(self.enrich_callbacks_by_events, callback)])


class NotificationsEndpoint(object):

    def __init__(self, enrich_callback_by_events, enqueue_callback):
        self.enrich_callbacks_by_events = enrich_callback_by_events
        self.enqueue_callback = enqueue_callback

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        for event_string in self.enrich_callbacks_by_events:
            if str(event_type) == event_string:

                callbacks = self.enrich_callbacks_by_events[event_string]
                enriched_events = []
                for callback in callbacks:
                    result = callback(payload, event_type)
                    if isinstance(result, list):
                        enriched_events += result
                    else:
                        enriched_events.append(result)
                self._enqueue_events(enriched_events)

    def _enqueue_events(self, enriched_events):
        for event in enriched_events:
            if event is not None:
                self.enqueue_callback(event_type='', data=event)
                LOG.debug('EVENT ENQUEUED: \n' + str(event))
