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
# WARRANTIES OR  CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import copy

from debtcollector import removals
from oslo_log import log

from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.common.constants import GraphAction
from vitrage.datasources.driver_base import DriverBase
from vitrage.datasources.static.driver import StaticDriver
from vitrage.datasources.static import StaticFields
from vitrage.datasources.static_physical import STATIC_PHYSICAL_DATASOURCE
from vitrage.utils import file as file_utils

LOG = log.getLogger(__name__)


class StaticPhysicalDriver(DriverBase):
    @staticmethod
    def get_event_types():
        return []

    def enrich_event(self, event, event_type):
        pass

    ENTITIES_SECTION = 'entities'

    def __init__(self, conf):
        removals.removed_module(__name__, "datasources.static")
        super(StaticPhysicalDriver, self).__init__()
        self.cfg = conf
        self.cache = {}

    def get_all(self, datasource_action):
        return self.make_pickleable(self._get_all_entities(),
                                    STATIC_PHYSICAL_DATASOURCE,
                                    datasource_action)

    def get_changes(self, datasource_action):
        LOG.info(datasource_action)
        return self.make_pickleable(self._get_changes_entities(),
                                    STATIC_PHYSICAL_DATASOURCE,
                                    datasource_action)

    def _get_all_entities(self):
        static_entities = []

        files = file_utils.list_files(
            self.cfg.static_physical.directory, '.yaml')

        for file_ in files:
            full_path = self.cfg.static_physical.directory \
                + '/' + file_
            static_entities += self._get_entities_from_file(file_,
                                                            full_path)

        return static_entities

    def _get_entities_from_file(self, file_, path):
        static_entities = []
        config = file_utils.load_yaml_file(path)

        if StaticDriver._is_valid_config(config):
            LOG.warning("Skipped config of new static datasource: {}"
                        .format(file_))
            return []

        for entity in config[self.ENTITIES_SECTION]:
            static_entities.append(entity.copy())

        self.cache[file_] = config

        return static_entities

    def _get_changes_entities(self):

        entities_updates = []
        files = file_utils.list_files(
            self.cfg.static_physical.directory, '.yaml')

        for file_ in files:
            full_path = self.cfg.static_physical.directory +\
                '/' + file_
            config = file_utils.load_yaml_file(full_path)

            if StaticDriver._is_valid_config(config):
                LOG.warning("Skipped config of new static datasource: {}"
                            .format(file_))
                return []

            if config:
                if file_ in self.cache:
                    if str(config) != str(self.cache[file_]):
                        # TODO(alexey_weyl): need also to remove deleted
                        #                   files from cache
                        old_config = copy.deepcopy(config)

                        self._update_on_existing_entities(
                            self.cache[file_][self.ENTITIES_SECTION],
                            config[self.ENTITIES_SECTION],
                            entities_updates)

                        self._update_on_new_entities(
                            config[self.ENTITIES_SECTION],
                            self.cache[file_][self.ENTITIES_SECTION],
                            entities_updates)

                        self.cache[file_] = old_config
                else:
                    self.cache[file_] = config
                    entities_updates += \
                        self._get_entities_from_file(file_, full_path)

        # iterate over deleted files
        deleted_files = set(self.cache.keys()) - set(files)
        for file_ in deleted_files:
            self._update_on_existing_entities(
                self.cache[file_][self.ENTITIES_SECTION],
                {},
                entities_updates)
            del self.cache[file_]

        return entities_updates

    def _update_on_existing_entities(self,
                                     old_entities,
                                     new_entities,
                                     updates):
        for old_entity in old_entities:
            if not new_entities or old_entity not in new_entities:
                new_entity = self._find_entity(old_entity, new_entities)
                if not new_entity:
                    self._set_event_type(old_entity, GraphAction.DELETE_ENTITY)
                    updates.append(old_entity.copy())
                else:
                    self._set_event_type(new_entity, GraphAction.UPDATE_ENTITY)
                    updates.append(new_entity.copy())

    @staticmethod
    def _find_entity(new_entity, entities):
        for entity in entities:
            if entity[StaticFields.TYPE] == new_entity[StaticFields.TYPE] \
                    and entity[StaticFields.ID] == new_entity[StaticFields.ID]:
                return entity
        return None

    @staticmethod
    def _update_on_new_entities(new_entities, old_entities, updates):
        for entity in new_entities:
            if entity not in updates and entity not in old_entities:
                updates.append(entity.copy())

    @staticmethod
    def _set_event_type(entity, event_type):
        entity[DSProps.EVENT_TYPE] = event_type
