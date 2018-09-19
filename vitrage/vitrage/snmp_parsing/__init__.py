# Copyright 2017 - ZTE
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
    cfg.IntOpt('snmp_listening_port',
               default=8162,
               help='The listening port of snmp_parsing service'),
    cfg.StrOpt('oid_mapping',
               default='',
               help='The default path of oid_mapping yaml file.'),
    ]
