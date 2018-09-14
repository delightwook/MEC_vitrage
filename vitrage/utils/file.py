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

import os

from oslo_log import log
import yaml

LOG = log.getLogger(__name__)


def list_files(dir_path,
               suffix=None,
               with_pathname=False,
               with_exception=False):
    if not os.path.isdir(dir_path):
        return []

    try:
        file_list = os.listdir(dir_path)
    except Exception as e:
        if with_exception:
            raise
        else:
            LOG.error("Fails to list files in %s: %s" % (dir_path, e))
            return []
    if suffix:
        file_list = [os.path.join(dir_path, f) if with_pathname else f
                     for f in file_list if f.endswith(suffix)]

    return file_list


def load_yaml_files(dir_path, with_exception=False):
    files = list_files(dir_path, '.yaml', with_pathname=True)

    yaml_files = []
    for f in files:
        config = load_yaml_file(f, with_exception)
        if config:
            yaml_files.append(config)

    return yaml_files


def load_yaml_file(full_path, with_exception=False):
    if not os.path.isfile(full_path):
        LOG.error("File doesn't exist: %s." % full_path)
        return None

    with open(full_path, 'r') as stream:
        try:
            return yaml.load(stream, Loader=yaml.BaseLoader)
        except Exception as e:
            if with_exception:
                raise
            else:
                LOG.error("Fails to parse file: %s. %s" % (full_path, e))
                return None
