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
    cfg.ListOpt('plugins',
                help='Names of enabled machine learning plugins '
                     '(example jaccard_correlation)'),
    cfg.ListOpt('plugins_path',
                default=['vitrage.machine_learning.plugins'],
                help='list of base path for notifiers'),
    cfg.StrOpt('machine_learning_topic',
               default='vitrage.machine_learning',
               help='The topic that vitrage-graph uses for graph '
                    'machine learning messages.'),
    ]
