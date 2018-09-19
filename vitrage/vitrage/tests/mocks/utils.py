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

import codecs
from collections import namedtuple
import json
from os.path import dirname
from os import walk


def store_specs(spec, target_filename, target_folder=None):
    """Stores specs in JSON format.

    :param spec: specification of trace generator
    :param target_filename: name of file to save in
    :param target_folder: folder for file. defaults to "resources"
    :return: full path to target file
    """

    target = _get_full_path(target_filename, target_folder)
    with open(target, 'w') as outfile:
        json.dump(spec, outfile, sort_keys=True, indent=4, ensure_ascii=False)
    return target


def load_specs(target_filename, target_folder=None):
    """Loads JSON from file in target location. Defaults to "resources" folder

    :param target_filename:
    :param target_folder:
    :return:
    """

    target = _get_full_path(target_filename, target_folder)
    reader = codecs.getreader("utf-8")
    with open(target, "rb") as infile:
        return json.load(reader(infile))


def get_def_templates_dict_from_list(def_temps_list):
    """Turns a list of def_temps into a dictionary of def_temps where the keys

    are their index in the list. Used by unit tests

    :param def_temps_list: def_temp list to convert
    :type def_temps_list: list
    :return: a def_temps dict
    :rtype: dict
    """

    Template = namedtuple('Template', 'data')
    dict = {}
    for num, item in zip(range(len(def_temps_list)), def_temps_list):
        dict[num] = Template(item)

    return dict


def _get_full_path(target_filename, target_folder):
    """Returns the full path for the given folder and filename

    :param target_filename: filename to search. Can be None.
    :param target_folder: folder to search. If None, defaults to "resources"
    :return: full path for the given info
    """

    if target_folder is None:
        target_folder = '%s/mock_configurations/driver' % \
                        get_resources_dir()
    target = '{0}/{1}'.format(target_folder, target_filename)
    return target


def get_resources_dir(filename=None, target_folder='resources'):
    """Locates the resources directory dynamically.

    :param filename: file to locate in directory
    :param target_folder: name of folder.
    :return: path to resources directory
    """

    parent_dir = dirname(dirname(__file__))
    for dir_path, _, file_names in walk(parent_dir):
        if target_folder in dir_path and  \
                (filename is None or filename in file_names):
            return dir_path


def generate_vals(param_specs):
    """Generate values from specs.

    :param param_specs: dictionary where the value is in regex format
    :return: dictionary with generated values for regexs
    """

    if isinstance(param_specs, dict):
        current_info = {k: generate_vals(v) for k, v in param_specs.items()}
    elif isinstance(param_specs, list) or isinstance(param_specs, tuple):
        # convert tuples to lists
        current_info = [generate_vals(param) for param in param_specs]
    elif param_specs:  # assumes primitive type
        current_info = str(param_specs)
    else:
        current_info = None
    return current_info


def merge_vals(current, update):
    """Update the current container with updated values.

    Supports dictionary, list and basic types, as well as nesting.
    :param current: the container to update
    :param update: the container to update with
    :return: updated container
    """

    if current is None:  # value previously not in "current"
        return update
    if isinstance(update, dict):
        for k in update:
            current[k] = merge_vals(current.get(k, None), update[k])
    elif isinstance(update, list):
        # assumes the update is <= from current - use nicely!
        for i in range(len(update)):
            if i < len(current):
                current[i] = merge_vals(current[i], update[i])
            else:
                current.append(update[i])
    else:
        current = update
    return current
