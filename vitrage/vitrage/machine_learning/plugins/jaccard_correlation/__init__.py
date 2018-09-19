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

from oslo_config import cfg

OPTS = [
    cfg.StrOpt('plugin_path',
               default='vitrage.machine_learning.plugins.'
                       'jaccard_correlation.alarm_processor.'
                       'AlarmDataProcessor',
               help='jaccard_correlation class path',
               required=True),
    cfg.IntOpt('num_of_events_to_flush', default=1000,
               help='the amount of events flushes'),
    cfg.StrOpt('output_folder', default='/tmp',
               help='folder to write all reports to'),
    cfg.FloatOpt('correlation_threshold', default=0,
                 help='threshold of interesting correlations'),
    cfg.FloatOpt('high_corr_score', default=0.9,
                 help='high correlation lower limit'),
    cfg.FloatOpt('med_corr_score', default=0.5,
                 help='medium correlation lower limit'),
    ]
