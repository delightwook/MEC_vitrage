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
from concurrent.futures import ThreadPoolExecutor
from futurist import periodics

from oslo_log import log
from vitrage.datasources import utils

from vitrage.common.constants import DatasourceAction
from vitrage.common.utils import spawn

from vitrage.entity_graph.consistency.consistency_enforcer import\
    ConsistencyEnforcer
from vitrage.entity_graph import datasource_rpc as ds_rpc
from vitrage.persistency.graph_persistor import GraphPersistor

LOG = log.getLogger(__name__)


class Scheduler(object):

    def __init__(self, conf, graph, events_coordination):
        super(Scheduler, self).__init__()
        self.conf = conf
        self.graph = graph
        self.events_coordination = events_coordination
        self.graph_persistor = GraphPersistor(conf) if \
            self.conf.persistency.enable_persistency else None
        self.consistency = ConsistencyEnforcer(conf, graph)
        self.periodic = None

    def start_periodic_tasks(self):
        self.periodic = periodics.PeriodicWorker.create(
            [], executor_factory=lambda: ThreadPoolExecutor(max_workers=10))

        self.add_persist_timer()
        self.add_consistency_timer()
        self.add_rpc_datasources_timers()
        spawn(self.periodic.start)

    def add_persist_timer(self):
        if not self.graph_persistor:
            return
        spacing = self.conf.persistency.graph_persistency_interval

        @periodics.periodic(spacing=spacing)
        def persist_periodic():
            if self.graph_persistor:
                try:
                    self.graph_persistor.store_graph(graph=self.graph)
                except Exception:
                    LOG.exception('Persist failed.')

        self.periodic.add(persist_periodic)
        LOG.info("added persist_periodic (spacing=%s)", spacing)

    def add_consistency_timer(self):
        spacing = self.conf.datasources.snapshots_interval

        @periodics.periodic(spacing=spacing)
        def consistency_periodic():
            try:
                self.consistency.periodic_process()
            except Exception:
                LOG.exception('run_consistency failed.')

        self.periodic.add(consistency_periodic)
        LOG.info("added consistency_periodic (spacing=%s)", spacing)

    def add_rpc_datasources_timers(self):
        spacing = self.conf.datasources.snapshots_interval
        rpc_client = ds_rpc.create_rpc_client_instance(self.conf)

        @periodics.periodic(spacing=spacing)
        def get_all_periodic():
            try:
                ds_rpc.get_all(rpc_client,
                               self.events_coordination,
                               self.conf.datasources.types,
                               DatasourceAction.SNAPSHOT)
            except Exception:
                LOG.exception('get_all_periodic failed.')

        self.periodic.add(get_all_periodic)
        LOG.info("added get_all_periodic (spacing=%s)", spacing)

        driver_names = utils.get_pull_drivers_names(self.conf)
        for d_name in driver_names:
            spacing = self.conf[d_name].changes_interval
            rpc_client = ds_rpc.create_rpc_client_instance(self.conf)

            @periodics.periodic(spacing=spacing)
            def get_changes_periodic(driver_name=d_name):
                try:
                    ds_rpc.get_changes(rpc_client,
                                       self.events_coordination,
                                       driver_name)
                except Exception:
                    LOG.exception('get_changes_periodic "%s" failed.',
                                  driver_name)

            self.periodic.add(get_changes_periodic)
            LOG.info("added get_changes_periodic %s (spacing=%s)",
                     d_name, spacing)
