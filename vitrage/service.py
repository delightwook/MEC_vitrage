# Copyright 2015 - Alcatel-Lucent
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
from oslo_db import options as db_options
from oslo_log import log
from oslo_policy import opts as policy_opts
from osprofiler import initializer as osprofiler_initializer
from osprofiler import opts as osprofiler_opts
from vitrage import keystone_client
from vitrage import messaging
from vitrage import opts
from vitrage.opts import register_opts


LOG = log.getLogger(__name__)


def prepare_service(args=None, conf=None, config_files=None):
    if conf is None:
        conf = cfg.ConfigOpts()
    log.register_options(conf)
    policy_opts.set_defaults(conf)
    osprofiler_opts.set_defaults(conf)
    db_options.set_defaults(conf)

    for group, options in opts.list_opts():
        conf.register_opts(list(options),
                           group=None if group == 'DEFAULT' else group)

    conf(args, project='vitrage', validate_default_values=True,
         default_config_files=config_files)

    if conf.profiler.enabled:
        osprofiler_initializer.init_from_conf(
            conf=conf,
            context=None,
            project="vitrage",
            service="api",
            host=conf.api.host)

    for datasource in conf.datasources.types:
        register_opts(conf, datasource, conf.datasources.path)

    keystone_client.register_keystoneauth_opts(conf)

    log.setup(conf, 'vitrage')
    conf.log_opt_values(LOG, log.DEBUG)
    messaging.setup()

    return conf
