# Copyright 2017 - Nokia
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

from oslo_log import log
import oslo_messaging

from vitrage.messaging import get_transport


LOG = log.getLogger(__name__)


class CollectorNotifier(object):
    """Allows writing to message bus"""
    def __init__(self, conf):
        self.oslo_notifier = None
        try:
            topics = [conf.datasources.notification_topic_collector]
            if conf.persistency.enable_persistency:
                topics.append(conf.persistency.persistor_topic)
            else:
                LOG.warning("Not persisting events")

            self.oslo_notifier = oslo_messaging.Notifier(
                get_transport(conf),
                driver='messagingv2',
                publisher_id='datasources.events',
                topics=topics)
        except Exception as e:
            LOG.info('Collector notifier - missing configuration %s'
                     % str(e))

    @property
    def enabled(self):
        return self.oslo_notifier is not None

    def notify_when_applicable(self, enriched_event):
        """Callback subscribed to driver.graph updates

        :param enriched_event: the event with enriched data added by the driver
        """

        try:
            self.oslo_notifier.info({}, '', enriched_event)
        except Exception:
            LOG.exception('Datasource event cannot be notified - %s.',
                          enriched_event)
