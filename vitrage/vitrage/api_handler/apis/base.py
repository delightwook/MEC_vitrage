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

from oslo_log import log

from vitrage.common.constants import EdgeProperties as EProps
from vitrage.common.constants import EntityCategory
from vitrage.common.constants import VertexProperties as VProps
from vitrage.datasources.nova.host import NOVA_HOST_DATASOURCE
from vitrage.datasources.nova.instance import NOVA_INSTANCE_DATASOURCE
from vitrage.datasources.nova.zone import NOVA_ZONE_DATASOURCE
from vitrage.datasources import OPENSTACK_CLUSTER
from vitrage.graph import Direction
from vitrage.keystone_client import get_client as ks_client

LOG = log.getLogger(__name__)


# Used for Sunburst to show only specific resources
TREE_TOPOLOGY_QUERY = {
    'and': [
        {'==': {VProps.VITRAGE_CATEGORY: EntityCategory.RESOURCE}},
        {'==': {VProps.VITRAGE_IS_DELETED: False}},
        {'==': {VProps.VITRAGE_IS_PLACEHOLDER: False}},
        {
            'or': [
                {'==': {VProps.VITRAGE_TYPE: OPENSTACK_CLUSTER}},
                {'==': {VProps.VITRAGE_TYPE: NOVA_INSTANCE_DATASOURCE}},
                {'==': {VProps.VITRAGE_TYPE: NOVA_HOST_DATASOURCE}},
                {'==': {VProps.VITRAGE_TYPE: NOVA_ZONE_DATASOURCE}}
            ]
        }
    ]
}

TOPOLOGY_AND_ALARMS_QUERY = {
    'and': [
        {'==': {VProps.VITRAGE_IS_DELETED: False}},
        {'==': {VProps.VITRAGE_IS_PLACEHOLDER: False}},
        {
            'or': [
                {'==': {VProps.VITRAGE_CATEGORY: EntityCategory.ALARM}},
                {'==': {VProps.VITRAGE_CATEGORY: EntityCategory.RESOURCE}}
            ]
        }
    ]
}

RCA_QUERY = {
    'and': [
        {'==': {VProps.VITRAGE_CATEGORY: EntityCategory.ALARM}},
        {'==': {VProps.VITRAGE_IS_DELETED: False}}
    ]
}

ALARMS_ALL_QUERY = {
    'and': [
        {'==': {VProps.VITRAGE_CATEGORY: EntityCategory.ALARM}},
        {'==': {VProps.VITRAGE_IS_DELETED: False}}
    ]
}

ALARM_QUERY = {
    VProps.VITRAGE_CATEGORY: EntityCategory.ALARM,
    VProps.VITRAGE_IS_DELETED: False,
    VProps.VITRAGE_IS_PLACEHOLDER: False
}

EDGE_QUERY = {'==': {EProps.VITRAGE_IS_DELETED: False}}

RESOURCES_ALL_QUERY = {
    'and': [
        {'==': {VProps.VITRAGE_CATEGORY: EntityCategory.RESOURCE}},
        {'==': {VProps.VITRAGE_IS_DELETED: False}},
        {'==': {VProps.VITRAGE_IS_PLACEHOLDER: False}}
    ]
}


class EntityGraphApisBase(object):

    @classmethod
    def _get_query_with_project(cls, vitrage_category, project_id, is_admin):
        """Generate query with tenant data

        Creates query for entity graph which takes into consideration the
        vitrage_category, project_id and if the tenant is admin

        :type vitrage_category: string
        :type project_id: string
        :type is_admin: boolean
        :rtype: dictionary
        """

        query = {
            'and': [
                {'==': {VProps.VITRAGE_IS_DELETED: False}},
                {'==': {VProps.VITRAGE_IS_PLACEHOLDER: False}},
                {'==': {VProps.VITRAGE_CATEGORY: vitrage_category}}
            ]
        }

        cls._add_project_to_query(query, project_id, is_admin)

        return query

    @staticmethod
    def _add_project_to_query(query, project_id, is_admin):
        """Add project_id filter to the query

        Each query should contain the project_id condition

        :type query: string representing a json query
        :type project_id: string
        :type is_admin: boolean
        :rtype: string representing a json query
        """

        if is_admin:
            project_query = \
                {'or': [{'==': {VProps.PROJECT_ID: project_id}},
                        {'==': {VProps.PROJECT_ID: None}}]}
        else:
            project_query = \
                {'==': {VProps.PROJECT_ID: project_id}}

        if 'and' in query:
            query_with_project_id = query
            query_with_project_id['and'].append(project_query)
        else:
            query_with_project_id = {'and': [project_query, query]}

        return query_with_project_id

    def _filter_alarms(self, alarms, project_id):
        """Remove wrong alarms from the list

        Removes alarms where the project_id of the resource they sit on is
        different than the project_id sent as a parameter

        :type alarms: list
        :type project_id: string
        :rtype: list
        """

        alarms_to_remove = []

        for alarm in alarms:
            alarm_project_id = alarm.get(VProps.PROJECT_ID, None)
            if not alarm_project_id:
                cat_filter = {VProps.VITRAGE_CATEGORY: EntityCategory.RESOURCE}
                alarms_resource = \
                    self.entity_graph.neighbors(alarm.vertex_id,
                                                vertex_attr_filter=cat_filter)
                if len(alarms_resource) > 0:
                    resource_project_id = \
                        alarms_resource[0].get(VProps.PROJECT_ID, None)
                    if resource_project_id and \
                            resource_project_id != project_id:
                        alarms_to_remove.append(alarm)
            elif alarm_project_id != project_id:
                alarms_to_remove.append(alarm)

        return [x for x in alarms if x not in alarms_to_remove]

    def _is_alarm_of_current_project(self,
                                     entity,
                                     project_id,
                                     is_admin_project):
        """Checks if the alarm is of the current tenant

        Checks:
        1. checks if the project_id is the same
        2. if the tenant is admin then the projectid can be also None
        3. check the project_id of the resource where the alarm sits is the
           same as the project_id sent as a parameter

        :type entity: vertex
        :type project_id: string
        :type is_admin_project: boolean
        :rtype: boolean
        """

        current_project_id = entity.get(VProps.PROJECT_ID, None)
        if current_project_id == project_id:
            return True
        elif not current_project_id and is_admin_project:
            return True
        else:
            entities = self.entity_graph.neighbors(entity.vertex_id,
                                                   direction=Direction.OUT)
            for entity in entities:
                if entity[VProps.VITRAGE_CATEGORY] == EntityCategory.RESOURCE:
                    resource_project_id = entity.get(VProps.PROJECT_ID)
                    if resource_project_id == project_id or \
                            (not resource_project_id and is_admin_project):
                        return True
                    return False
            return False

    @staticmethod
    def _get_first(lst):
        if len(lst) == 1:
            return lst[0]
        else:
            return None

    def _is_project_admin(self, project_id):
        keystone_client = ks_client(self.conf)
        project = keystone_client.projects.get(project_id)
        return 'name=admin' in project.to_dict()
