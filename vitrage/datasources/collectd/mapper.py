# Copyright 2017 - Nokia
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

import re

from vitrage.datasources.collectd.properties \
    import CollectdProperties as CProps

COLLECTD_HOST_PARAM = '${collectd_host}'


class CollectdMapper(object):

    def __init__(self, mapping):
        self.mapping = mapping

    def find(self, collectd_name):
        resource_value = self.mapping.get(collectd_name)
        if resource_value:
            return \
                {
                    CProps.RESOURCE_TYPE: resource_value[CProps.RESOURCE_TYPE],
                    CProps.RESOURCE_NAME: resource_value[CProps.RESOURCE_NAME]
                }
        return self.find_regex(collectd_name)

    def find_regex(self, collectd_name):
        for pattern, value in self.mapping.items():
            if re.match(pattern, collectd_name):
                type_, name = \
                    value[CProps.RESOURCE_TYPE], value[CProps.RESOURCE_NAME]
                if name == COLLECTD_HOST_PARAM:
                    return \
                        {
                            CProps.RESOURCE_TYPE: type_,
                            CProps.RESOURCE_NAME: collectd_name
                        }
                else:
                    return \
                        {
                            CProps.RESOURCE_TYPE: type_,
                            CProps.RESOURCE_NAME: name
                        }
        raise KeyError(collectd_name)
