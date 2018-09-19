# Copyright 2018 - Nokia
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

from collections import namedtuple
from oslo_log import log

from vitrage.common.constants import DatasourceAction
from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.datasources.alarm_driver_base import AlarmDriverBase
from vitrage.datasources.prometheus import PROMETHEUS_DATASOURCE
from vitrage.datasources.prometheus.properties import get_alarm_update_time
from vitrage.datasources.prometheus.properties import get_label
from vitrage.datasources.prometheus.properties import PrometheusAlertStatus \
    as PAlertStatus
from vitrage.datasources.prometheus.properties import PrometheusLabels \
    as PLabels
from vitrage.datasources.prometheus.properties import PrometheusProperties \
    as PProps

LOG = log.getLogger(__name__)

PROMETHEUS_EVENT_TYPE = 'prometheus.alarm'


class PrometheusDriver(AlarmDriverBase):
    AlarmKey = namedtuple('AlarmKey', ['alert_name', 'instance'])

    def __init__(self, conf):
        super(PrometheusDriver, self).__init__()
        self.conf = conf
        self._client = None

    def _vitrage_type(self):
        return PROMETHEUS_DATASOURCE

    def _alarm_key(self, alarm):
        return self.AlarmKey(alert_name=get_label(alarm, PLabels.ALERT_NAME),
                             instance=str(get_label(alarm, PLabels.INSTANCE)))

    def _is_erroneous(self, alarm):
        return alarm and PAlertStatus.FIRING == alarm.get(PProps.STATUS)

    def _is_valid(self, alarm):
        if not alarm or PProps.STATUS not in alarm:
            return False
        return True

    def _status_changed(self, new_alarm, old_alarm):
        return new_alarm.get(PProps.STATUS) != old_alarm.get(PProps.STATUS)

    def _get_alarms(self):
        # TODO(iafek): should be implemented
        return []

    def enrich_event(self, event, event_type):
        """Get an event from Prometheus and create a list of alarm events

        :param event: dictionary of this form:
            {
              "status": "firing",
              "groupLabels": {
                "alertname": "HighInodeUsage"
              },
              "groupKey": "{}:{alertname=\"HighInodeUsage\"}",
              "commonAnnotations": {
                "mount_point": "/%",
                "description": "\"Consider ssh\"ing into the instance \"\n",
                "title": "High number of inode usage",
                "value": "96.81%",
                "device": "/dev/vda1%",
                "runbook": "troubleshooting/filesystem_alerts_inodes.md"
              },
              "alerts": [
                {
                  "status": "firing",
                  "labels": {
                    "severity": "critical",
                    "fstype": "ext4",
                    "instance": "localhost:9100",
                    "job": "node",
                    "alertname": "HighInodeUsage",
                    "device": "/dev/vda1",
                    "mountpoint": "/"
                  },
                  "endsAt": "0001-01-01T00:00:00Z",
                  "generatorURL": "http://devstack-rocky-4:9090/graph?g0.htm1",
                  "startsAt": "2018-05-03T12:25:38.231388525Z",
                  "annotations": {
                    "mount_point": "/%",
                    "description": "\"Consider ssh\"ing into the instance\"\n",
                    "title": "High number of inode usage",
                    "value": "96.81%",
                    "device": "/dev/vda1%",
                    "runbook": "troubleshooting/filesystem_alerts_inodes.md"
                  }
                }
              ],
              "version": "4",
              "receiver": "vitrage",
              "externalURL": "http://devstack-rocky-4:9093",
              "commonLabels": {
                "severity": "critical",
                "fstype": "ext4",
                "instance": "localhost:9100",
                "job": "node",
                "alertname": "HighInodeUsage",
                "device": "/dev/vda1",
                "mountpoint": "/"
              }
            }

        :param event_type: The type of the event. Always 'prometheus.alarm'.
        :return: a list of events, one per Prometheus alert

        """

        LOG.debug('Going to enrich event: %s', str(event))

        alarms = []

        for alarm in event.get(PProps.ALERTS, []):
            alarm[DSProps.EVENT_TYPE] = event_type
            alarm[PProps.STATUS] = event[PProps.STATUS]

            old_alarm = self._old_alarm(alarm)
            alarm = self._filter_and_cache_alarm(alarm, old_alarm,
                                                 self._filter_get_erroneous,
                                                 get_alarm_update_time(alarm))

            if alarm:
                alarms.append(alarm)

        LOG.debug('Enriched event. Created alarm events: %s', str(alarms))

        return self.make_pickleable(alarms, PROMETHEUS_DATASOURCE,
                                    DatasourceAction.UPDATE)

    @staticmethod
    def get_event_types():
        return [PROMETHEUS_EVENT_TYPE]
