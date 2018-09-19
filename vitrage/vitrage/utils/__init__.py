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

from oslo_config import cfg


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
