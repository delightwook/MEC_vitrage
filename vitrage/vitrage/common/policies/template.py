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

TEMPLATE = 'template %s'

rules = [
    policy.DocumentedRuleDefault(
        name=TEMPLATE % 'delete',
        check_str=base.UNPROTECTED,
        description='Delete a template',
        operations=[
            {
                'path': '/template',
                'method': 'DELETE'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=TEMPLATE % 'add',
        check_str=base.UNPROTECTED,
        description='Add a template',
        operations=[
            {
                'path': '/template',
                'method': 'PUT'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=TEMPLATE % 'validate',
        check_str=base.UNPROTECTED,
        description='Validate a template, or all templates in a folder',
        operations=[
            {
                'path': '/template',
                'method': 'POST'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=TEMPLATE % 'list',
        check_str=base.UNPROTECTED,
        description='List all templates',
        operations=[
            {
                'path': '/template',
                'method': 'GET'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=TEMPLATE % 'show',
        check_str=base.UNPROTECTED,
        description='Show the template body for given template ID',
        operations=[
            {
                'path': '/template/{template_uuid}',
                'method': 'GET'
            }
        ]
    )
]


def list_rules():
    return rules
