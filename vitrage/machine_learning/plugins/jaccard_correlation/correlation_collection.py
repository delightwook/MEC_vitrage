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

from collections import defaultdict
from itertools import groupby
from operator import itemgetter
from oslo_log import log

LOG = log.getLogger(__name__)


class CorrelationPriorities(object):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AlarmsProperties(object):
    ALARM1_RESOURCE_ID = 0
    ALARM1_RESOURCE_TYPE = 1
    ALARM1_NAME = 2
    ALARM2_RESOURCE_ID = 3
    ALARM2_RESOURCE_TYPE = 4
    ALARM2_NAME = 5
    OFFSET_DELTA = 6
    CORR_SCORE = 7


class CorrelationCollection(object):

    def __init__(self, high_corr_score, med_corr_score):
        self.correlation_list = []
        self.high_corr_score = high_corr_score
        self.med_corr_score = med_corr_score

    def set(self, alarm_1, alarm_2, offset_delta, correlation_score):

        self.correlation_list.append(alarm_1 + alarm_2 +
                                     (offset_delta, correlation_score))

    def get_aggregated(self):

        pairs_dict = defaultdict(list)

        for alarm_pair in self.correlation_list:
            if ((alarm_pair[AlarmsProperties.ALARM1_RESOURCE_TYPE],
                 alarm_pair[AlarmsProperties.ALARM1_NAME],
                 alarm_pair[AlarmsProperties.ALARM2_RESOURCE_TYPE],
                 alarm_pair[AlarmsProperties.ALARM2_NAME])) in pairs_dict:

                pairs_dict[alarm_pair[AlarmsProperties.ALARM1_RESOURCE_TYPE],
                           alarm_pair[AlarmsProperties.ALARM1_NAME],
                           alarm_pair[AlarmsProperties.ALARM2_RESOURCE_TYPE],
                           alarm_pair[AlarmsProperties.ALARM2_NAME]]\
                    .append(alarm_pair[AlarmsProperties.CORR_SCORE])
            else:
                pairs_dict[alarm_pair[AlarmsProperties.ALARM2_RESOURCE_TYPE],
                           alarm_pair[AlarmsProperties.ALARM2_NAME],
                           alarm_pair[AlarmsProperties.ALARM1_RESOURCE_TYPE],
                           alarm_pair[AlarmsProperties.ALARM1_NAME]].\
                    append(alarm_pair[AlarmsProperties.CORR_SCORE])

        results = [(key, sum((pairs_dict[key])) / float(len(pairs_dict[key])))
                   for key in pairs_dict]

        categorize = lambda x: CorrelationPriorities.HIGH \
            if x[1] >= self.high_corr_score \
            else CorrelationPriorities.MEDIUM \
            if x[1] >= self.med_corr_score else CorrelationPriorities.LOW

        return [(key, [(x, y) for x, y in group]) for
                key, group in groupby(sorted(results, key=itemgetter(1)),
                                      key=categorize)]
