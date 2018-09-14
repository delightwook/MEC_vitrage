# Copyright 2016 - Nokia
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

from oslo_config import cfg


# Register options for the service
OPTS = [
    cfg.StrOpt('evaluator_notification_topic_prefix',
               default='vitrage_evaluator_notifications',
               help='A prefix of the topic on which events will be sent from '
                    'the evaluator to the specific notifiers')
]
