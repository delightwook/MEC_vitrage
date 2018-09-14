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

from collections import namedtuple
from oslo_log import log
import pickle

LOG = log.getLogger(__name__)

AccumulatedData = namedtuple('AccumulatedData', ['activity', 'intersection'])

ACTIVITY_PATH = "/tmp/alarms_activity.txt"
INTERSECT_PATH = "/tmp/alarms_intersections.txt"


def load_data():
    try:
        with open(ACTIVITY_PATH, 'rb') as activity_f:
            alarms_activity = pickle.load(activity_f)
    except Exception as e:
        LOG.info('Cannot load alarms_activity - %s', e)
        return AccumulatedData({}, {})

    try:
        with open(INTERSECT_PATH, 'rb') as intersect_f:
            alarms_intersect = pickle.load(intersect_f)
    except Exception as e:
        LOG.info('Cannot load alarms_intersect - %s', e)
        return AccumulatedData({}, {})

    return AccumulatedData(alarms_activity, alarms_intersect)


def save_accumulated_data(data_manager):
    activity = data_manager.alarms_activity
    intersects = data_manager.alarms_intersects

    try:
        with open(ACTIVITY_PATH, 'wb') as activity_f:
            pickle.dump(activity, activity_f)
    except Exception:
        LOG.exception('Cannot save alarms_intersect.')

    try:
        with open(INTERSECT_PATH, 'wb') as intersect_f:
            pickle.dump(intersects, intersect_f)
    except Exception:
        LOG.exception('Cannot save alarms_intersect.')
