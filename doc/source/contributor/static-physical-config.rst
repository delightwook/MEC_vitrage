===================================================
(Obsolete) Static Physical Datasource Configuration
===================================================

Overview
--------

The Static Physical datasource allows users to integrate the physical topology
into Vitrage. Physical topology includes switches and their connection to
other switches and physical hosts.

This datasource is static - pre-configured in a file. This is sufficient in
many cases where the physical topology is relatively unchanging.

Configure Access to Static Physical
-----------------------------------

The following should be set in **/etc/vitrage/vitrage.conf**, under
[static_physical] section:

+------------------+---------------------------------------------------------+----------------------------------+
| Name             | Description                                             | Default Value                    |
+==================+=========================================================+==================================+
| directory        | Directory path from where to load the configurations    | /etc/vitrage/static_datasources/ |
+------------------+---------------------------------------------------------+----------------------------------+
| changes_interval | Interval of checking changes in the configuration files | 30 seconds                       |
+------------------+---------------------------------------------------------+----------------------------------+
| entities         | Static physical entity types list                       | switch                           |
+------------------+---------------------------------------------------------+----------------------------------+


Configure Static Physical Mapping
---------------------------------

Physical configuration is made for configuring statically physical entities,
and their relationships to other entities in the topology.

Some physical entities, such as switches, can not be retrieved from OpenStack,
and so are defined here.

There may be more than one configuration file. All files will be read from
*/etc/vitrage/static_datasources/*. See previous section on how to configure this
location.

Format
++++++

.. code::

  entities:
    - name: <Physical entity name as appears in configuration>
      id: <Physical entity id as appears in configuration>
      type: <Physical entity type - see below for details>
      state: <default resource state>
      relationships:
        - type: <Physical entity type it is connected to - see below for details>
          name: <Name of physical entity as appears in configuration>
          id: <Id of physical entity as appears in configuration>
          relation_type: <Relation name>
        - type: ...
  ...


Notes:
  - The "type" key must match the name of a type from an existing datasource.
  - Type names appear, for each datasource, in its __init__.py file.
  - For example see */workspace/dev/vitrage/vitrage/datasources/nova/host/__init__.py*


Example
+++++++

The following will define a switch that is attached to host-1 and is a backup
of switch-2

.. code::

  entities:
    - type: switch
      name: switch-1
      id: switch-1 # should be same as name
      state: available
      relationships:
        - type: nova.host
          name: host-1
          id: host-1 # should be same as name
          relation_type: attached
        - type: switch
          name: switch-2
          id: switch-2 # should be same as name
          relation_type: backup

