# Copyright 2018 - Nokia
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

from __future__ import print_function

from oslo_log import log

from dateutil import parser
from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.graph.driver.networkx_graph import NXGraph
from vitrage import storage
from vitrage.storage.sqlalchemy import models
from vitrage.utils import datetime
from vitrage.utils.datetime import utcnow


LOG = log.getLogger(__name__)


class GraphPersistor(object):
    def __init__(self, conf):
        super(GraphPersistor, self).__init__()
        self.db_connection = storage.get_connection_from_config(conf)
        self.last_event_timestamp = datetime.datetime.utcnow()

    def store_graph(self, graph):
        LOG.info('Graph persistency running..')
        try:
            graph_snapshot = graph.write_gpickle()
            db_row = models.GraphSnapshot(
                last_event_timestamp=self.last_event_timestamp,
                graph_snapshot=graph_snapshot)
            self.db_connection.graph_snapshots.create(db_row)
        except Exception as e:
            LOG.exception("Graph is not stored: %s", e)

    def load_graph(self, timestamp=None):
        db_row = self.db_connection.graph_snapshots.query(timestamp) if \
            timestamp else self.db_connection.graph_snapshots.query(utcnow())
        return NXGraph.read_gpickle(db_row.graph_snapshot) if db_row else None

    def delete_graph_snapshots(self, timestamp):
        """Deletes all graph snapshots until timestamp"""
        self.db_connection.graph_snapshots.delete(timestamp)

    def update_last_event_timestamp(self, event):
        timestamp = event.get(DSProps.SAMPLE_DATE)
        self.last_event_timestamp = parser.parse(timestamp) if timestamp \
            else None
