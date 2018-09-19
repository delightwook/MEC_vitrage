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

from oslo_config import cfg

from vitrage.tests.functional.base import \
    TestFunctionalBase


class TestProcessorFunctional(TestFunctionalBase):

    ZONE_SPEC = 'ZONE_SPEC'
    HOST_SPEC = 'HOST_SPEC'
    INSTANCE_SPEC = 'INSTANCE_SPEC'

    # noinspection PyAttributeOutsideInit,PyPep8Naming
    @classmethod
    def setUpClass(cls):
        super(TestProcessorFunctional, cls).setUpClass()
        cls.conf = cfg.ConfigOpts()
        cls.conf.register_opts(cls.PROCESSOR_OPTS, group='entity_graph')
        cls.conf.register_opts(cls.DATASOURCES_OPTS, group='datasources')
        cls.load_datasources(cls.conf)

    def test_create_entity_graph(self):
        processor = self._create_processor_with_graph(self.conf)

        self.assertEqual(self._num_total_expected_vertices(),
                         processor.entity_graph.num_vertices())

        self.assertEqual(self._num_total_expected_edges(),
                         processor.entity_graph.num_edges())

        # TODO(Alexey): add this check and to check also the number of edges
        # check all entities create a tree and no free floating vertices exists
        # it will be done only after we will have zone plugin
        # vertex = graph.find_vertex_in_graph()
        # bfs_list = graph.algo.bfs(graph)
        # self.assertEqual(num_vertices, len(bfs_list))
