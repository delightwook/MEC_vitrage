# Copyright 2017 - Nokia
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
from oslo_log import log

LOG = log.getLogger(__name__)


class TemplateSchemaFactory(object):

    DEFAULT_VERSION = '1'
    _schemas = dict()

    @classmethod
    def supported_versions(cls):
        return cls._schemas.keys()

    @classmethod
    def is_version_supported(cls, version):
        return version in cls._schemas

    @classmethod
    def template_schema(cls, version):
        if not version:
            version = cls.DEFAULT_VERSION
        template_schema = cls._schemas.get(version)
        return template_schema

    @classmethod
    def register_template_schema(cls, version, template_schema):
        cls._schemas[version] = template_schema
        LOG.debug('Registered template schema for version %s', version)
