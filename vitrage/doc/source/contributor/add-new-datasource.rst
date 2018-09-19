==================
Add New Datasource
==================

Add Datasource Package - HOW TO
-------------------------------

In order to add a new datasource to Vitrage do the following steps:

 1. Have your datasource enclosed in a package with the datasources' name and
    put it under 'vitrage.datasources', For example:
    ``vitrage.datasource.cinder.volume``.
 2. Under your datasource package, have both your datasources' driver class
    and your datasources' transformer class. See below for details on those
    classes.
 3. Under your datasources' package ``__init__.py`` you must import ``cfg``
    from ``oslo_config`` and declare a list named ``OPTS``. Under ``OPTS``, you can define
    your needed options using the ``oslo_config.cfg`` module.
    There are three options you must have:

    a. Driver and transformer with the path to your driver and transformer
       classes respectively.
    b. ``update_method`` property that describes the vitrage_type of update mechanism for
       this datasource. The options are (string): push, pull or none.
    c. In addition to those three, you may add any other configuration options
       you may need for your datasource.

 4. In case you want your datasource to get registered under other names i.e.
    for other sub-entities, add a list option named 'entities' under which
    list all of your sub-entities names (more details below).
 5. In case you want your datasource to be automatically configured when
    devstack is installed, you need to add it to the 'types' property in the
    datasources section in the configuration. To do so, do the following:

    a. add the datasource name to the types property in the ``devstack.settings``
       file.
    b. if the datasource is not one of the main and basic projects of devstack,
       add the following data in the ``devstack.plugin.sh`` file":

    .. code:: bash

        # remove <datasource_name> vitrage datasource if <datasource_name> datasource not installed

        if ! is_service_enabled <datasource_name>; then
            disable_vitrage_datasource <datasource_name>
        fi
 6. You are done!


Driver Class
____________

Responsible for importing information regarding entities in the cloud.
Entities in this context refer both to resources (physical, virtual,
applicative) and alarms (Aodh, Nagios, Zabbix, Monasca, etc.)
The datasource has two modes of action:

 1. ``get_all`` (snapshot): Query all entities and send events to the vitrage
    events queue.
    When done for the first time, send an "end" event to inform it has finished
    the get_all for the datasource (because it is done asynchronously).
 2. ``notify``: Send an event to the vitrage events queue upon any change.
    This can be done in two ways:

    a. Built in polling mechanism called ``get_changes``.
    b. Built in pushing mechanism using the oslo bus.

A driver should inherit from 'vitrage.datasources.driver_base.DriverBase' class
and must implement the following methods:

+----------------------+------------------------------------+--------------------------------+--------------------------------+
| Name                 | Input                              | Output                         | Comments                       |
+======================+====================================+================================+================================+
| get_all              | action type                        | entities                       | for snapshot mechanism         |
+----------------------+------------------------------------+--------------------------------+--------------------------------+
| get_changes          | action type                        | entities                       | for update pulling mechanism   |
+----------------------+------------------------------------+--------------------------------+--------------------------------+
| get_event_types      |                                    | event types                    | for update pushing mechanism   |
+----------------------+------------------------------------+--------------------------------+--------------------------------+
| enrich_event         | event, event_type                  | entity event                   | for update pushing mechanism   |
+----------------------+------------------------------------+--------------------------------+--------------------------------+


Transformer Class
_________________

The Transformer class understands the specific entity details and outputs a
tuple with the following details:

 1. The vertex with its new details to be added/updated/deleted.
 2. List of tuples where each tuple consists of:

    a. Neighbor vertex with it's partial data so vitrage will know to where
       to connect the edge.
    b. Edge that connects the vertex to its neighbor.

Note that for every driver there should be a matching Transformer.
A transformer should inherit from
``vitrage.datasources.transformer_base.TransformerBase`` class and
must implement the following methods:

+----------------------------------+------------------------------------+----------------------------------------+
| Name                             | Input                              | Output                                 |
+==================================+====================================+========================================+
| _create_snapshot_entity_vertex   | entity event                       | vertex                                 |
+----------------------------------+------------------------------------+----------------------------------------+
| _create_update_entity_vertex     | entity event                       | vertex                                 |
+----------------------------------+------------------------------------+----------------------------------------+
| _create_snapshot_neighbors       | entity event                       | neighbor tuple                         |
+----------------------------------+------------------------------------+----------------------------------------+
| _create_update_neighbors         | entity event                       | neighbor tuple                         |
+----------------------------------+------------------------------------+----------------------------------------+
| _create_entity_key               | entity event                       | the unique key of this entity          |
+----------------------------------+------------------------------------+----------------------------------------+
| get_type                         |                                    | datasources type                       |
+----------------------------------+------------------------------------+----------------------------------------+


Configuration
_____________

Holds the following fields:

+----------------------------+------------------------------------+-------------------------------------------------------------+
| Name                       | Type                               | Description                                                 |
+============================+====================================+=============================================================+
| transformer                | string - Required!                 | Transformer class path under vitrage                        |
+----------------------------+------------------------------------+-------------------------------------------------------------+
| driver                     | string - Required!                 | Driver class path under vitrage                             |
+----------------------------+------------------------------------+-------------------------------------------------------------+
| update_method              | string - Required!                 | need to be one of: pull, push or none values                |
+----------------------------+------------------------------------+-------------------------------------------------------------+
| changes_interval           | integer - Optional                 | Interval between checking for changes in polling mechanism  |
+----------------------------+------------------------------------+-------------------------------------------------------------+
| entities                   | string list - Optional             | Sub-entities of the datasource                              |
+----------------------------+------------------------------------+-------------------------------------------------------------+

**Example**

Datasource ``__init__.py OPTS``:

.. code:: python

    from oslo_config import cfg

    OPTS = [
        cfg.StrOpt('transformer',
                   default='vitrage.datasources.cinder.volume.transformer.'
                           'CinderVolumeTransformer',
                   help='Cinder volume transformer class path',
                   required=True),
        cfg.StrOpt('driver',
                   default='vitrage.datasources.cinder.volume.driver.'
                           'CinderVolumeDriver',
                   help='Cinder volume driver class path',
                   required=True),
        cfg.StrOpt('update_method',
               default=UpdateMethod.PUSH,
               help='None: updates only via Vitrage periodic snapshots.'
                    'Pull: updates every [changes_interval] seconds.'
                    'Push: updates by getting notifications from the'
                    ' datasource itself.',
               required=True),
    ]


Instantiation flow
------------------

Now, when loading Vitrage, ``vitrage.datasources.launcher.Launcher``
will get instantiated and will register all of the datasources
into Vitrage. **Note**: if you want your datasource to also run as a
service i.e. get changes every <interval> you need to set under your
datasources ``OPTS`` an ``Integer`` option named ``changes_interval``.

Additionally, ``vitrage.entity_graph.transformer_manager.TransformerManager``
will get instantiated and will register all of the datasources transformers
into Vitrage.

These two steps are using your previously configured driver and
transformer path options under your datasources' package ``__init__.OPTS``.


Datasource Configuration Options
--------------------------------

Any option your datasource defined can be accessed using ``oslo_config.cfg``
or by configuring ``vitrage.conf``.

**Example**

.. code:: python

    cfg.<datasource_name>.<option_name>


**Example**

.. code::

    # /etc/vitrage/vitrage.conf
    ...
    [datasources]
    snapshots_interval = 300
    # Names of supported plugins (list value)
    types = zabbix,nova.host,nova.instance,nova.zone,static,aodh,cinder.volume,neutron.network,neutron.port,heat.stack

    [zabbix]
    url = http://<ip>/zabbix
    password = zabbix
    user = admin
    config_file = /etc/vitrage/zabbix_conf.yaml

    [nagios]
    user = omdadmin
    password = omd
    url = http://<ip>:<port>/<site>/nagios/cgi-bin/status.cgi
    config_file = /etc/vitrage/nagios_conf.yaml


Using the scaffold tool
-----------------------

A datasource scaffold tool is provided to get you started to create a new
datasource. See ``tools\datasoruce-scaffold`` for details.

This tool uses `cookiecutter`_ to generate the scaffold of new datasource.

.. _cookiecutter: https://github.com/audreyr/cookiecutter

**Install**

.. code-block:: shell

    pip install -r requirements.txt

**Usage**

.. code-block:: shell

    $ cookiecutter .
    name [sample]:

Enter the name of new datasource. It will create a new folder in current
directory including the scaffold of the new data source. Move the directory to
``vitrage/datasources`` as a start point for a complete implemenation.
