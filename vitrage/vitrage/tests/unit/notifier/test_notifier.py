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

"""
test_vitrage graph
----------------------------------

Tests for `vitrage` graph driver
"""

import copy

from vitrage.common.constants import EntityCategory
from vitrage.common.constants import NotifierEventTypes as NType
from vitrage.common.constants import VertexProperties as VProps
from vitrage.datasources.nova.host import NOVA_HOST_DATASOURCE
from vitrage.entity_graph.processor.notifier import _get_notification_type
from vitrage.evaluator.actions import evaluator_event_transformer as evaluator
from vitrage.graph import Vertex
from vitrage.tests import base


resource = Vertex('123', {
    VProps.VITRAGE_CATEGORY: EntityCategory.RESOURCE,
    VProps.VITRAGE_TYPE: 'some_resource_type',
    VProps.VITRAGE_IS_DELETED: False,
    VProps.VITRAGE_IS_PLACEHOLDER: False,
    })

deduced_alarm = Vertex('123', {
    VProps.VITRAGE_CATEGORY: EntityCategory.ALARM,
    VProps.VITRAGE_TYPE: evaluator.VITRAGE_DATASOURCE,
    VProps.VITRAGE_IS_DELETED: False,
    VProps.VITRAGE_IS_PLACEHOLDER: False,
    })


non_deduced_alarm = Vertex('123', {
    VProps.VITRAGE_CATEGORY: EntityCategory.ALARM,
    VProps.VITRAGE_TYPE: 'TEST_ALARM',
    VProps.VITRAGE_IS_DELETED: False,
    VProps.VITRAGE_IS_PLACEHOLDER: True,
    })

deleted_alarm = Vertex('123', {
    VProps.VITRAGE_CATEGORY: EntityCategory.ALARM,
    VProps.VITRAGE_TYPE: evaluator.VITRAGE_DATASOURCE,
    VProps.VITRAGE_IS_DELETED: True,
    VProps.VITRAGE_IS_PLACEHOLDER: False,
    })

placeholder_alarm = Vertex('123', {
    VProps.VITRAGE_CATEGORY: EntityCategory.ALARM,
    VProps.VITRAGE_TYPE: evaluator.VITRAGE_DATASOURCE,
    VProps.VITRAGE_IS_DELETED: False,
    VProps.VITRAGE_IS_PLACEHOLDER: True,
    })


host = Vertex('123', {
    VProps.VITRAGE_CATEGORY: EntityCategory.RESOURCE,
    VProps.VITRAGE_TYPE: NOVA_HOST_DATASOURCE,
    VProps.VITRAGE_IS_DELETED: False,
    VProps.VITRAGE_IS_PLACEHOLDER: False,
    })

forced_down_host = Vertex('123', {
    VProps.VITRAGE_CATEGORY: EntityCategory.RESOURCE,
    VProps.VITRAGE_TYPE: NOVA_HOST_DATASOURCE,
    VProps.VITRAGE_IS_DELETED: False,
    VProps.VITRAGE_IS_PLACEHOLDER: False,
    VProps.IS_MARKED_DOWN: True,
    })


class GraphTest(base.BaseTest):
    def get_first(self, lst):
        self.assertIsNotNone(lst)
        return lst[0] if len(lst) > 0 else None

    def test_notification_type_new_alarm(self):
        ret = _get_notification_type(None, deduced_alarm, True)
        self.assertEqual(NType.ACTIVATE_DEDUCED_ALARM_EVENT,
                         self.get_first(ret),
                         'new alarm should notify activate')

        ret = _get_notification_type(None, non_deduced_alarm, True)
        self.assertIsNone(self.get_first(ret),
                          'alarm that is not a deduced alarm')

    def test_notification_type_deleted_alarm(self):
        ret = _get_notification_type(deduced_alarm, deleted_alarm, True)
        self.assertEqual(NType.DEACTIVATE_DEDUCED_ALARM_EVENT,
                         self.get_first(ret),
                         'deleted alarm should notify deactivate')

    def test_notification_type_resource_vertex(self):
        ret = _get_notification_type(None, resource, True)
        self.assertIsNone(self.get_first(ret),
                          'any non alarm vertex should be ignored')

    def test_notification_type_updated_alarm(self):
        ret = _get_notification_type(deduced_alarm, deduced_alarm, True)
        self.assertIsNone(self.get_first(ret),
                          'A not new alarm vertex should be ignored')

        ret = _get_notification_type(deleted_alarm, deduced_alarm, True)
        self.assertEqual(NType.ACTIVATE_DEDUCED_ALARM_EVENT,
                         self.get_first(ret),
                         'old alarm become not deleted should notify activate')

        ret = _get_notification_type(placeholder_alarm, deduced_alarm, True)
        self.assertEqual(NType.ACTIVATE_DEDUCED_ALARM_EVENT,
                         self.get_first(ret),
                         'placeholder become active should notify activate')

    def test_notification_type_placeholder_alarm(self):
        ret = _get_notification_type(None, placeholder_alarm, True)
        self.assertIsNone(self.get_first(ret),
                          'A not new alarm vertex should be ignored')

    def test_notification_type_new_host(self):
        ret = _get_notification_type(None, forced_down_host, True)
        self.assertEqual(NType.ACTIVATE_MARK_DOWN_EVENT,
                         self.get_first(ret),
                         'new host with forced_down should notify activate')

        ret = _get_notification_type(None, host, True)
        self.assertIsNone(self.get_first(ret), 'host without forced_down')

    def test_notification_type_deleted_host(self):
        deleted_host = copy.deepcopy(forced_down_host)
        deleted_host[VProps.VITRAGE_IS_DELETED] = True
        ret = _get_notification_type(forced_down_host, deleted_host, True)
        self.assertEqual(
            NType.DEACTIVATE_MARK_DOWN_EVENT,
            self.get_first(ret),
            'deleted host with forced_down should notify deactivate')

        deleted_host = copy.deepcopy(host)
        deleted_host[VProps.VITRAGE_IS_DELETED] = True
        ret = _get_notification_type(forced_down_host, deleted_host, True)
        self.assertEqual(
            NType.DEACTIVATE_MARK_DOWN_EVENT,
            self.get_first(ret),
            'deleted host with forced_down should notify deactivate')

        deleted_host = copy.deepcopy(host)
        deleted_host[VProps.VITRAGE_IS_DELETED] = True
        ret = _get_notification_type(host, deleted_host, True)
        self.assertIsNone(
            self.get_first(ret),
            'deleted host without forced_down should not notify')

    def test_notification_type_updated_host(self):
        ret = _get_notification_type(forced_down_host, forced_down_host, True)
        self.assertIsNone(self.get_first(ret),
                          'A not new host should be ignored')

        deleted_host = copy.deepcopy(forced_down_host)
        deleted_host[VProps.VITRAGE_IS_DELETED] = True
        ret = _get_notification_type(deleted_host, forced_down_host, True)
        self.assertEqual(NType.ACTIVATE_MARK_DOWN_EVENT,
                         self.get_first(ret),
                         'old host become not deleted should notify activate')

        deleted_host = copy.deepcopy(forced_down_host)
        deleted_host[VProps.VITRAGE_IS_DELETED] = True
        ret = _get_notification_type(deleted_host, host, True)
        self.assertIsNone(self.get_first(ret),
                          'old host become not deleted should not notify')

        placeholder_host = copy.deepcopy(forced_down_host)
        placeholder_host[VProps.VITRAGE_IS_PLACEHOLDER] = True
        ret = _get_notification_type(placeholder_host, forced_down_host, True)
        self.assertEqual(NType.ACTIVATE_MARK_DOWN_EVENT,
                         self.get_first(ret),
                         'placeholder become active should notify activate')

    def test_notification_type_placeholder_host(self):
        placeholder_host = copy.deepcopy(forced_down_host)
        placeholder_host[VProps.VITRAGE_IS_PLACEHOLDER] = True
        ret = _get_notification_type(None, placeholder_host, True)
        self.assertIsNone(self.get_first(ret),
                          'A not new host vertex should be ignored')
