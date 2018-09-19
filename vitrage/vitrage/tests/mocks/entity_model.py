# Copyright 2015 - Alcatel-Lucent
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


from vitrage.tests.mocks.utils import generate_vals
from vitrage.tests.mocks.utils import merge_vals


class BasicEntityModel(object):
    """A representation of the events generated for an entity.

    Events consist of static information that does not change between events,
    and dynamic information that is generated via regex.
    """

    def __init__(self, dynamic_vals, static_vals=None):
        self.static_vals = static_vals
        self.param_specs = dynamic_vals

    @property
    def params(self):
        """Returns a sample event of this entity.

        :return: a sample event of this entity
        :rtype: dict
        """
        dynamic_vals = generate_vals(self.param_specs)
        if self.static_vals:
            return merge_vals(dynamic_vals, self.static_vals)
        else:
            return dynamic_vals
