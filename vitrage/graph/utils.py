# Copyright 2016 - Alcatel-Lucent
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
from vitrage.common.constants import EdgeProperties as EConst
from vitrage.common.constants import VertexProperties as VConst
from vitrage.graph.driver.elements import Edge
from vitrage.graph.driver.elements import Vertex


def create_vertex(vitrage_id,
                  vitrage_category=None,
                  vitrage_type=None,
                  vitrage_sample_timestamp=None,
                  vitrage_is_deleted=False,
                  vitrage_is_placeholder=False,
                  entity_id=None,
                  entity_state=None,
                  update_timestamp=None,
                  project_id=None,
                  metadata=None):
    """A builder to create a vertex

    :param vitrage_id:
    :type vitrage_id: str
    :param entity_id:
    :type entity_id: str
    :param vitrage_category:
    :type vitrage_category: str
    :param vitrage_type:
    :type vitrage_type: str
    :param entity_state:
    :type entity_state: str
    :param vitrage_is_deleted:
    :type vitrage_is_deleted: boolean
    :param update_timestamp:
    :type update_timestamp: str
    :param vitrage_sample_timestamp:
    :type vitrage_sample_timestamp: str
    :param metadata:
    :type metadata: dict
    :param vitrage_is_placeholder:
    :type vitrage_is_placeholder: boolean
    :param project_id:
    :type project_id: str
    :return:
    :rtype: Vertex
    """

    properties = {
        VConst.ID: entity_id,
        VConst.STATE: entity_state,
        VConst.VITRAGE_TYPE: vitrage_type,
        VConst.VITRAGE_CATEGORY: vitrage_category,
        VConst.VITRAGE_IS_DELETED: vitrage_is_deleted,
        VConst.UPDATE_TIMESTAMP: update_timestamp,
        VConst.VITRAGE_SAMPLE_TIMESTAMP: vitrage_sample_timestamp,
        VConst.VITRAGE_IS_PLACEHOLDER: vitrage_is_placeholder,
        VConst.VITRAGE_ID: vitrage_id,
        VConst.PROJECT_ID: project_id
    }
    if metadata:
        properties.update(metadata)
    properties = {k: v for k, v in properties.items() if v is not None}
    vertex = Vertex(vertex_id=vitrage_id, properties=properties)
    return vertex


def create_edge(source_id,
                target_id,
                relationship_type,
                vitrage_is_deleted=False,
                update_timestamp=None,
                metadata=None):
    """A builder to create an edge

    :param update_timestamp:
    :param source_id:
    :type source_id: str
    :param target_id:
    :type target_id: str
    :param relationship_type:
    :type relationship_type: str
    :param vitrage_is_deleted:
    :type vitrage_is_deleted: str
    :param metadata:
    :type metadata: dict
    :return:
    :rtype: Edge
    """
    properties = {
        EConst.UPDATE_TIMESTAMP: update_timestamp,
        EConst.VITRAGE_IS_DELETED: vitrage_is_deleted,
        EConst.RELATIONSHIP_TYPE: relationship_type,
    }
    if metadata:
        properties.update(metadata)
    properties = {k: v for k, v in properties.items() if v is not None}
    edge = Edge(source_id=source_id,
                target_id=target_id,
                label=relationship_type,
                properties=properties)
    return edge


def check_property_with_regex(key, regex, data):
    """Checks if the contents of data[key] matches the given regex

    :param: key: key to find in data
    :param: data: dict to search
    :type: data: dict
    :param: regex: regular expression to check against
    :type: regex: str
    :rtype: bool
    """
    value = data.get(key)
    if value is None:
        return False
    pattern = re.compile(regex)
    return pattern.match(value) is not None
