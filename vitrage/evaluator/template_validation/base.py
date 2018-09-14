# Copyright 2016 - Nokia
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
from collections import namedtuple
from vitrage.evaluator.template_validation.status_messages import status_msgs

Result = namedtuple('Result', ['description', 'is_valid_config', 'status_code',
                               'comment'])


def get_correct_result(description):
    return Result(description, True, 0, status_msgs[0])


def get_warning_result(description, code):
    return Result(description, True, code, status_msgs[code])


def get_fault_result(description, code, msg=None):
    if msg:
        return Result(description, False, code, msg)
    return Result(description, False, code, status_msgs[code])
