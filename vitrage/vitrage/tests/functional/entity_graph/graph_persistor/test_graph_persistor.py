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
import sys
import time

from oslo_config import cfg
from oslo_db.options import database_opts

from vitrage.persistency.graph_persistor import GraphPersistor
from vitrage import storage
from vitrage.storage.sqlalchemy import models
from vitrage.tests.functional.base import TestFunctionalBase
from vitrage.tests.mocks.graph_generator import GraphGenerator
from vitrage.utils.datetime import utcnow


class TestGraphPersistor(TestFunctionalBase):

    # noinspection PyAttributeOutsideInit,PyPep8Naming
    @classmethod
    def setUpClass(cls):
        super(TestGraphPersistor, cls).setUpClass()
        cls.conf = cfg.ConfigOpts()
        cls.conf.register_opts(cls.PROCESSOR_OPTS, group='entity_graph')
        cls.conf.register_opts(cls.DATASOURCES_OPTS, group='datasources')
        cls.conf.register_opts(database_opts, group='database')
        cls.conf.set_override('connection', 'sqlite:///test-%s.db'
                              % sys.version_info[0], group='database')
        cls._db = storage.get_connection_from_config(cls.conf)
        engine = cls._db._engine_facade.get_engine()
        models.Base.metadata.create_all(engine)
        cls.load_datasources(cls.conf)
        cls.graph_persistor = GraphPersistor(cls.conf)

    def test_persist_graph(self):
        g = GraphGenerator().create_graph()
        current_time = utcnow()
        self.graph_persistor.last_event_timestamp = current_time
        self.graph_persistor.store_graph(g)
        graph_snapshot = self.graph_persistor.load_graph(current_time)
        self.assert_graph_equal(g, graph_snapshot)
        self.graph_persistor.delete_graph_snapshots(utcnow())

    def test_persist_two_graphs(self):
        g1 = GraphGenerator().create_graph()
        current_time1 = utcnow()
        self.graph_persistor.last_event_timestamp = current_time1
        self.graph_persistor.store_graph(g1)
        graph_snapshot1 = self.graph_persistor.load_graph(current_time1)

        g2 = GraphGenerator(5).create_graph()
        current_time2 = utcnow()
        self.graph_persistor.last_event_timestamp = current_time2
        self.graph_persistor.store_graph(g2)
        graph_snapshot2 = self.graph_persistor.load_graph(current_time2)

        self.assert_graph_equal(g1, graph_snapshot1)
        self.assert_graph_equal(g2, graph_snapshot2)
        self.graph_persistor.delete_graph_snapshots(utcnow())

    def test_load_last_graph_snapshot_until_timestamp(self):
        g1 = GraphGenerator().create_graph()
        self.graph_persistor.last_event_timestamp = utcnow()
        self.graph_persistor.store_graph(g1)

        time.sleep(1)
        time_in_between = utcnow()
        time.sleep(1)

        g2 = GraphGenerator(5).create_graph()
        self.graph_persistor.last_event_timestamp = utcnow()
        self.graph_persistor.store_graph(g2)

        graph_snapshot = self.graph_persistor.load_graph(time_in_between)
        self.assert_graph_equal(g1, graph_snapshot)
        self.graph_persistor.delete_graph_snapshots(utcnow())

    def test_delete_graph_snapshots(self):
        g = GraphGenerator().create_graph()
        self.graph_persistor.last_event_timestamp = utcnow()
        self.graph_persistor.store_graph(g)
        self.graph_persistor.delete_graph_snapshots(utcnow())
        graph_snapshot = self.graph_persistor.load_graph(utcnow())
        self.assertIsNone(graph_snapshot)
