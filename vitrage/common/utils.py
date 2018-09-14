# -*- encoding: utf-8 -*-
# Copyright 2015 - Alcatel-Lucent
# Copyright © 2014-2015 eNovance
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2011 Justin Santa Barbara
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
from collections import defaultdict
import copy
import itertools
import random
import threading

from oslo_config import cfg

import cProfile


def recursive_keypairs(d, separator='.'):
    # taken from ceilometer and gnocchi
    for name, value in sorted(d.items()):
        if isinstance(value, dict):
            for subname, subvalue in recursive_keypairs(value, separator):
                yield ('%s%s%s' % (name, separator, subname), subvalue)
        else:
            yield name, value


def opt_exists(conf_parent, opt):
    try:
        return conf_parent[opt]
    except cfg.NoSuchOptError:
        return False


def do_cprofile(func):
    def profiled_func(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            return result
        finally:
            profile.print_stats('cumulative')
    return profiled_func


def get_portion(lst, num_of_portions, portion_index):
    """Split a list into n slices and return the i'th slice

    :rtype: list
    """
    # First shuffle the items to create an even distribution
    # Use the same random seed to always get the same shuffle
    if num_of_portions < 1 or portion_index < 0 or \
            portion_index >= num_of_portions:
        raise Exception('Cannot get_portion %s %s',
                        str(num_of_portions),
                        str(portion_index))

    list_copy = copy.copy(lst)
    random.Random(0.5).shuffle(list_copy)

    portions = defaultdict(list)
    portion_indexes = range(num_of_portions)
    g = itertools.cycle(portion_indexes)
    for curr_item in list_copy:
        curr_portion = next(g)
        portions[curr_portion].append(curr_item)
    return portions[portion_index]


def spawn(target, *args, **kwargs):
    t = threading.Thread(target=target, args=args, kwargs=kwargs)
    t.daemon = True
    t.start()
    return t
