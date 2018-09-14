# Copyright 2018 - Nokia Corporation
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

from oslo_policy import policy

from vitrage.common.policies import base

webhook = 'webhook %s'

rules = [
    policy.DocumentedRuleDefault(
        name=webhook % 'delete',
        check_str=base.UNPROTECTED,
        description='Delete a webhook registration',
        operations=[
            {
                'path': '/webhook/{webhook_id}',
                'method': 'DELETE'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=webhook % 'list',
        check_str=base.UNPROTECTED,
        description='List all webhook registrations',
        operations=[
            {
                'path': '/webhook',
                'method': 'GET'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=webhook % 'list:all_tenants',
        check_str=base.ROLE_ADMIN,
        description='List all webhooks (if the user'
                    ' has the permissions)',
        operations=[
            {
                'path': '/webhook',
                'method': 'GET'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=webhook % 'show',
        check_str=base.UNPROTECTED,
        description='Show a webhook registration with a given id',
        operations=[
            {
                'path': '/webhook/{webhook_id}',
                'method': 'GET'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=webhook % 'add',
        check_str=base.UNPROTECTED,
        description='Add a webhook registration with given info',
        operations=[
            {
                'path': '/webhook',
                'method': 'POST'
            }
        ]
    )
]


def list_rules():
    return rules
