# Copyright 2016 - Nokia
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

import functools

from vitrage.graph.driver.elements import Vertex


def _before_func(graph, item):
    if not graph.is_subscribed():
        return
    return graph.get_item(item)


def _after_func(graph, item, data_before=None):
    if not graph.is_subscribed():
        return
    element = graph.get_item(item)
    is_vertex = isinstance(element, Vertex) or isinstance(item, Vertex)
    graph.notifier.notify(data_before, element, is_vertex, graph)


class Notifier(object):
    def __init__(self):
        self._subscriptions = []

    def subscribe(self, function):
        self._subscriptions.append(function)

    def is_subscribed(self):
        return len(self._subscriptions) != 0

    def notify(self, *args, **kwargs):
        for func in self._subscriptions:
            func(*args, **kwargs)

    @staticmethod
    def update_notify(func):
        @functools.wraps(func)
        def notified_func(graph, item, *args, **kwargs):
            data_before = _before_func(graph, item)
            func(graph, item, *args, **kwargs)
            _after_func(graph, item, data_before)
        return notified_func

    @staticmethod
    def add_notify(func):
        @functools.wraps(func)
        def notified_func(graph, item, *args, **kwargs):
            func(graph, item, *args, **kwargs)
            _after_func(graph, item)
        return notified_func
