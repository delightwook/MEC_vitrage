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

from vitrage.common.constants import VertexProperties as VProps


class PropsConverter(object):

    PROPS_CONVERSION = {
        'category': VProps.VITRAGE_CATEGORY,
        'type': VProps.VITRAGE_TYPE,
        'resource_id': VProps.VITRAGE_RESOURCE_ID,
        'sample_timestamp': VProps.VITRAGE_SAMPLE_TIMESTAMP,
        'is_deleted': VProps.VITRAGE_IS_DELETED,
        'is_placeholder': VProps.VITRAGE_IS_PLACEHOLDER,
        'aggregated_state': VProps.VITRAGE_AGGREGATED_STATE,
        'operational_state': VProps.VITRAGE_OPERATIONAL_STATE,
        'aggregated_severity': VProps.VITRAGE_AGGREGATED_SEVERITY,
        'operational_severity': VProps.VITRAGE_OPERATIONAL_SEVERITY
    }

    @classmethod
    def convert_props_with_set(cls, properties):
        converted_properties = set()
        for key, value in properties:
            new_key = cls.PROPS_CONVERSION[key] if key in \
                cls.PROPS_CONVERSION else key
            converted_properties.add((new_key, value))
        return converted_properties

    @classmethod
    def convert_props_with_dictionary(cls, properties):
        converted_properties = {}
        for key, value in properties.items():
            new_key = cls.PROPS_CONVERSION[key] if key in \
                cls.PROPS_CONVERSION else key
            converted_properties[new_key] = value
        return converted_properties
