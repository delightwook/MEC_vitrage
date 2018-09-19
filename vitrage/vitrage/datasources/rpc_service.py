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

from concurrent import futures
import time

from oslo_log import log

from vitrage.common.constants import DatasourceAction
from vitrage.datasources import utils
from vitrage.messaging import VitrageNotifier
from vitrage import rpc as vitrage_rpc

LOG = log.getLogger(__name__)


class CollectorRpcHandlerService(object):

    def __init__(self, conf):
        super(CollectorRpcHandlerService, self).__init__()
        self.conf = conf
        async_persistor = self.create_async_persistor(conf)
        self.server = vitrage_rpc.get_default_server(
            conf,
            conf.rpc_topic_collector,
            [DriversEndpoint(conf, async_persistor)])

    def start(self):
        LOG.info("Collector Rpc Handler Service - Starting...")
        self.server.start()
        LOG.info("Collector Rpc Handler Service - Started!")

    def stop(self):
        LOG.info("Collector Rpc Handler Service - Stopping...")
        self.server.stop()
        LOG.info("Collector Rpc Handler Service - Stopped!")

    @staticmethod
    def create_async_persistor(conf):
        if not conf.persistency.enable_persistency:
            return None
        topics = [conf.persistency.persistor_topic]
        notifier = VitrageNotifier(conf, 'driver.events', topics)
        persist_worker = futures.ThreadPoolExecutor(max_workers=1)

        def do_persist(events):
            for e in events:
                notifier.notify('', e)

        def do_work(events):
            persist_worker.submit(do_persist, events)

        return do_work


class DriversEndpoint(object):

    def __init__(self, conf, async_persistor):
        self.conf = conf
        self.async_persistor = async_persistor
        self.pool = futures.ThreadPoolExecutor(
            max_workers=len(self.conf.datasources.types))

    def driver_get_all(self, ctx, driver_names, action, retry_on_fault=False):
        """Call get_all for specified drivers"""
        LOG.debug("run drivers get_all: %s %s", driver_names, action)
        drivers = utils.get_drivers_by_name(self.conf, driver_names)
        fault_interval = self.conf.datasources.snapshot_interval_on_fault

        def run_driver(driver):
            try:
                return True, driver.get_all(action)
            except Exception:
                LOG.exception('Driver failed')
                return False, driver

        result = list(self.pool.map(run_driver, drivers))
        failed_drivers = [driver for success, driver in result if not success]
        if failed_drivers and retry_on_fault:
            LOG.info('retrying failed drivers in %s seconds', fault_interval)
            time.sleep(fault_interval)
            result.extend(list(self.pool.map(run_driver, failed_drivers)))

        events = [e for success, events in result if success for e in events]
        if self.async_persistor:
            self.async_persistor(events)
        LOG.debug("run drivers get_all done.")
        return events

    def driver_get_changes(self, ctx, driver_name):
        """Call get_changes for a specific driver"""
        LOG.debug("run driver get_changes: %s", driver_name)
        drivers = utils.get_drivers_by_name(self.conf, [driver_name])
        events = drivers[0].get_changes(DatasourceAction.UPDATE)
        if self.async_persistor:
            self.async_persistor(events)
        LOG.debug("run driver get_changes: %s done.", driver_name)
        return events
