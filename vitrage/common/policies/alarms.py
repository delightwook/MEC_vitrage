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

from oslo_policy import policy

from vitrage.common.policies import base

rules = [
    policy.DocumentedRuleDefault(
        name='get alarm',
        check_str=base.UNPROTECTED,
        description='Show the details of specified alarm',
        operations=[
            {
                'path': '/alarm',
                'method': 'GET'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name='list alarms',
        check_str=base.UNPROTECTED,
        description='List the alarms on a resource, or all alarms',
        operations=[
            {
                'path': '/alarm',
                'method': 'GET'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name='list alarms:all_tenants',
        check_str=base.ROLE_ADMIN,
        description='List alarms of all tenants '
                    '(if the user has the permissions)',
        operations=[
            {
                'path': '/alarm',
                'method': 'GET'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name='get alarms count',
        check_str=base.UNPROTECTED,
        description='Show how many alarms of each operations severity exist',
        operations=[
            {
                'path': '/alarm/count',
                'method': 'GET'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name='get alarms count:all_tenants',
        check_str=base.ROLE_ADMIN,
        description='Show how many alarms of each operation severity exist. '
                    'Consider the alarms of all tenants (if the user has the '
                    'permissions)',
        operations=[
            {
                'path': '/alarm/count',
                'method': 'GET'
            }
        ]
    )
]


def list_rules():
    return rules
