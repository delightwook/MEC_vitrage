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


class PrometheusProperties(object):
    STATUS = 'status'
    ALERTS = 'alerts'
    ANNOTATIONS = 'annotations'
    LABELS = 'labels'


class PrometheusAlertStatus(object):
    FIRING = 'firing'
    RESOLVED = 'resolved'


class PrometheusAlertProperties(object):
    STARTS_AT = 'startsAt'
    ENDS_AT = 'endsAt'


class PrometheusAnnotations(object):
    TITLE = 'title'             # A human friendly name of the alert


class PrometheusLabels(object):
    SEVERITY = 'severity'
    INSTANCE = 'instance'
    ALERT_NAME = 'alertname'    # A (unique?) name of the alert


def get_alarm_update_time(alarm):
    return alarm.get(PrometheusAlertProperties.ENDS_AT) if \
        PrometheusAlertProperties.ENDS_AT in alarm else \
        alarm.get(PrometheusAlertProperties.STARTS_AT)


def get_annotation(alarm, annotation):
    annotations = alarm.get(PrometheusProperties.ANNOTATIONS)
    return annotations.get(annotation) if annotations else None


def get_label(alarm, label):
    labels = alarm.get(PrometheusProperties.LABELS)
    return labels.get(label) if labels else None
