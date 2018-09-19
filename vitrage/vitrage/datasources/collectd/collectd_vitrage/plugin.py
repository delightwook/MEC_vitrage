# -*- coding: utf-8 -*-
#
# © 2013 Lyft, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.  You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Common code for collectd python plugins.
"""

import collectd


class CollectDPlugin(object):
    """Base class for collectd plugins written in Python.

    Each plugin must have a unique name which must match the name
    used for the configuration block in the collectd configuration file.
    """

    def __init__(self, name=None):
        self.name = name
        if name:
            collectd.register_config(self.configure, name=self.name)
        else:
            collectd.register_config(self.configure)
        collectd.register_init(self.initialize)
        collectd.register_shutdown(self.shutdown)

    @staticmethod
    def config_to_dict(config):
        """Convert a collectd.Config object to a dictionary. """

        def config_to_tuple(config):
            """Convert a collectd.Config object to a tuple. """

            if config.children:
                return (config.key, dict(config_to_tuple(child)
                                         for child in config.children))
            elif len(config.values) > 1:
                return config.key, config.values
            else:
                return config.key, config.values[0]

        return {k: v for k, v in [config_to_tuple(config)]}

    def error(self, message):
        """Log an error message to the collectd logger. """

        collectd.error('%s plugin: %s' % (self.name, message))

    def warning(self, message):
        """Log an warning message to the collectd logger. """

        collectd.warning('%s plugin: %s' % (self.name, message))

    def notice(self, message):
        """Log an notice message to the collectd logger. """

        collectd.notice('%s plugin: %s' % (self.name, message))

    def info(self, message):
        """Log an info message to the collectd logger. """

        collectd.info('%s plugin: %s' % (self.name, message))

    def debug(self, message):
        """Log an debug message to the collectd logger. """

        collectd.debug('%s plugin: %s' % (self.name, message))

    def configure(self, config, **kwargs):
        """Configuration callback for the plugin.

        will be called by collectd with a collectd.
        Config object containing configuration data for this plugin from the
        collectd configuration file.
        """

        # The top level of the configuration is the 'Module' block, which
        # is entirely useless, so we set the config attribute to its value,
        # which should be the interesting stuff.
        self.config = CollectDPlugin.config_to_dict(config)['Module']

    def initialize(self):
        """Initialization callback for the plugin.

        will be called by collectd with no arguments.
        """
        pass

    def shutdown(self):
        """Shutdown callback for the plugin.

        will be called by collectd with no arguments.
        """
        pass

    def add_read_callback(self, callback, **kwargs):
        """Register a read callback with collectd.

        kwargs will be passed to collectd.register_read.
        The callback will be called by collectd without arguments.
        """
        collectd.register_read(callback, **kwargs)

    def add_write_callback(self, callback, **kwargs):
        """Register a write callback with collectd.

        kwargs will be passed to collectd.register_read.
        The callback will be called by collectd with a collectd.
        Values object as the only argument.
        """

        collectd.register_write(callback)

    def add_flush_callback(self, callback, **kwargs):
        """Register a flush callback with collectd.

        kwargs will be passed to collectd.register_flush.
        The callback will be called by collectd with two arguments,
        a timeout and an identifier.
        """
        collectd.register_flush(callback, **kwargs)

    def add_log_callback(self, callback, **kwargs):
        """Register a log callback with collectd.

        kwargs will be passed to collectd.register_log.
        The callback will be called by collectd with two arguments,
        the severity and the message (without a newline at the end)
        """
        collectd.register_log(callback, **kwargs)

    def add_notification_callback(self, callback, **kwargs):
        """Register a notification callback with collectd.

        kwargs will be passed to collectd.register_notification.
        The callback will be called by collectd with a collectd.
        Notification object as the only argument.
        """
        collectd.register_notification(callback, **kwargs)


class PluginError(Exception):
    pass
