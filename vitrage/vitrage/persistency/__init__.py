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
    cfg.StrOpt('persistor_topic',
               default='vitrage_persistor',
               help='The topic on which event will be sent from the '
                    'datasources to the persistor'),
    cfg.BoolOpt('enable_persistency',
                default=False,
                help='Periodically store entity graph snapshot to database'),
    cfg.IntOpt('graph_persistency_interval',
               default=3600,
               help='Store graph to database every X seconds'),
    ]
