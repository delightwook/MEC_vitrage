===============================
Static Datasource Configuration
===============================

Overview
--------

The static datasource allows users to integrate the **unmanaged** resources and topology into Vitrage. Unmanaged means
the resource, relationship or property can not be retrieved from any API or database, except static configuration file.

This datasource is static - pre-configured in a file. This is sufficient in many cases where the resources and
relationship is relatively unchanging.

Static datasource suppresses the legacy static physical datasource. Theoretically both physical and virtual resources
and relationship between them can be configured in it.

Configure Access to Static
--------------------------

The following should be set in **/etc/vitrage/vitrage.conf**, under
``[static]`` section:

+------------------+---------------------------------------------------------+----------------------------------+
| Name             | Description                                             | Default Value                    |
+==================+=========================================================+==================================+
| directory        | Directory path from where to load the configurations    | /etc/vitrage/static_datasources/ |
+------------------+---------------------------------------------------------+----------------------------------+
| changes_interval | Interval of checking changes in the configuration files | 30 seconds                       |
+------------------+---------------------------------------------------------+----------------------------------+

Configure Static Mapping
------------------------

Static configuration is made for configuring statically managed resources, and their relationships to other resources
in the topology. Some physical resources, such as switches, can not be retrieved from OpenStack, and so are defined
here.

Static datasource use the same semantics as Vitrage template, except for the following extension

- Static resources are identified in Vitrage by ``static_id`` instead of ``template_id``
- Entity ``id`` must be specified to map the actual resource
- All entities configured in static datasource are considered ``RESOURCE``
- ``scenarios`` section is not applicable

There may be more than one configuration file. All files will be read from ``/etc/vitrage/static_datasources/``. See
previous section on how to configure this location.

Notes:
  - Static datasource shares the same configuration folder as legacy static physical datasource.
  - Both static configuration and legacy static physical configuration will be loaded in Ocata release.
  - The format is distinguished by checking existence of ``metadata`` key which is only available in static datasource.

Example
+++++++

.. code:: yaml

    metadata:
      name: # configuration name
      description: # configuration description
    definitions:
      entities:             # list of resources, note that alarms can not be defined for contrast with Vitrage template
        - static_id: s1     # unique ID in static datasource, it will be referred in relationship definition
          type: switch      # resource type, could be any string, not limited to the type from existing datasource.
          id: 12345         # resource ID, used together with ``type`` to refer a resource in real world
          name: switch-1    # name, state and other properties are considered as metadata of the resource
          state: active     # the state of the resource
          ...
        - static_id: h1
          type: nova.host   # resource type could be from existing datasource
          id: 1             # resource ID, used together with ``type`` to refer a resource in corresponding datasource
          state: active     # the state of the resource
          purpose: CI       # additional properties could be defined - if from existing datasource, it could be updated
          ...
      relationships:
        - source: s1                    # static ID of source entity
          target: h1                    # static ID of target entity
          relationship_type: attached   # relationship type, it will be used in scenario condition check
        ...

The example above defines a switch with ID ``12345`` attached to nova host with ID ``1``. The user also noted that this
host will be used for CI.
