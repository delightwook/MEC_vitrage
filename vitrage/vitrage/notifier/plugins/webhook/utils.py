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


def db_row_to_dict(row):

    return {
        'id': row.id,
        'project_id': row.project_id,
        'is_admin_webhook': row.is_admin_webhook,
        'created_at': row.created_at,
        'url': row.url,
        'regex_filter': row.regex_filter,
        'headers': row.headers
    }
