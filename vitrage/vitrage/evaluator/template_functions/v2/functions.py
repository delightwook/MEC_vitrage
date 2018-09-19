# Copyright 2018 - Nokia
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
from oslo_log import log

LOG = log.getLogger(__name__)

# Function names
GET_ATTR = 'get_attr'


def get_attr(match, *args):
    """Get the runtime value of an attribute of a template entity

    Usage: get_attr(template_id, attr_name)

    Example:

    scenario:
     condition: alarm_on_host_1
     actions:
       action:
         action_type: execute_mistral
         properties:
           workflow: demo_workflow
           input:
             host_name: get_attr(host_1,name)
             retries: 5

    get_attr(host_1, name) will return the name of the host that was matched
    by the evaluator to host_1

    :param match: The evaluator's match structure. A dictionary of
    {template_id, Vertex}
    :param args: The arguments of the function. For get_attr, the expected
    arguments are:
    - template_id: The internal template id of the entity
    - attr_name: The name of the wanted attribute
    :return: The wanted attribute if found, or None
    """

    if len(args) != 2:
        LOG.warning('Called function get_attr with wrong number of '
                    'arguments: %s. Usage: get_attr(vertex, attr_name)',
                    args)
        return

    template_id = args[0]
    attr_name = args[1]
    vertex = match.get(template_id)

    if not vertex:
        LOG.warning('Called function get_attr with unknown template_id %s',
                    args[0])
        return

    entity_props = vertex.properties
    attr = entity_props.get(attr_name) if entity_props else None

    if attr is None:
        LOG.warning('Attribute %s not found for vertex %s',
                    attr_name, str(vertex))

    LOG.debug('Function get_attr called with template_id %s and attr_name %s.'
              'Matched vertex properties: %s. Returned attribute value: %s',
              template_id, attr_name, str(entity_props), attr)

    return attr
