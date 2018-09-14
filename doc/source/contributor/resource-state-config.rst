============================
Resource State Configuration
============================

Overview
--------

Vitrage retrieves information from diverse data-sources regarding resources in
the cloud, and stores and combines this information into a unified system
model. An important property of a resource is its **state**. This state can
be used both in the Vitrage templates to trigger actions, and in the Horizon UI
for color-coding purposes. Therefore, it is important that within the Vitrage
data model, state names are aggregated and normalized.

Since each data-source might represent state differently, for each
data-source we can supply it's own mapping to the aggregated state supported
in Vitrage. This way we can know which state is more important.
In addition we also normalize the states for the horizon UI (called
vitrage_operational_state) in order for the UI to know what color to show in Horizon.
This page explains how to handle this mapping for a given
data-source.


Configure Access to Resource State
----------------------------------

The resource state configuration is handled via config files. The location of
these files can be determined in ``/etc/vitrage/vitrage.conf``. Under the
[entity_graph] section, set:

+------------------------+------------------------------------+----------------------------------+
| Name                   | Description                        | Default Value                    |
+========================+====================================+==================================+
| datasources_values_dir | Directory path from where to load  | /etc/vitrage/datasources_values/ |
|                        | the values configurations          |                                  |
+------------------------+------------------------------------+----------------------------------+


Configure Resource State Mapping
--------------------------------

The resource state configuration files configure how the state of each
resource is normalized. Some guidelines for creating a config file:

- Normalized state values, to which states should be mapped, can be found in
  normalized_resource_state.py (OperationalResourceState class).
- Each normalized state also comes with a priority, so
  that if a resource is given different states from different sources (e.g.,
  a host state set both by nagios and Vitrage), the state with the
  highest priority will be used as the **aggregated state**.
- The *UNRECOGNIZED* state will be used for states with no corresponding
  normalized state. This state *must* appear in the config file.
- The config file is in YAML format.
- The config filename must be <datasource name>.yaml, for the relevant
  datasource.
- Defining a config file for each datasource is recommended, but not mandatory.
  Datasources with no such configuration will use the values as-is.

Once the file is modified, you must restart **vitrage-graph** service to load
the changes.

Default Configuration
+++++++++++++++++++++

Default configurations for resource states will be installed with Vitrage for
all the pre-packaged data-sources.

Format
++++++

.. code:: yaml

  category: RESOURCE
  values:
    - aggregated values:
        priority: <Resource state priority - an integer>
        original values:
          - name: <Original resource state name>
            operational_value: <normalized resource state - from OperationalResourceState class>
          - name: ... # can list several states for one aggregation
    - aggregated values:
        priority: ... # can list several aggregated states
        ...
  ...


Example
+++++++

The following file will map resource states.

For aggregated state with priority 40 we have 4 states and each one of them is
mapped to operational severity ERROR.

For aggregated state with priority 30 we have 6 states and each one of them is
mapped to operational severity TRANSIENT, etc...

.. code :: yaml

  category: RESOURCE
    values:
      - aggregated values:
          priority: 40
          original values:
            - name: ERROR
              operational_value: ERROR
            - name: ERROR_DELETING
              operational_value: ERROR
            - name: ERROR_RESTORING
              operational_value: ERROR
            - name: ERROR_EXTENDING
              operational_value: ERROR
      - aggregated values:
          priority: 30
          original values:
            - name: CREATING
              operational_value: TRANSIENT
            - name: ATTACHING
              operational_value: TRANSIENT
            - name: DELETING
              operational_value: TRANSIENT
            - name: RESTORING-BACKUP
              operational_value: TRANSIENT
            - name: BACKING-UP
              operational_value: TRANSIENT
            - name: DETACHING
              operational_value: TRANSIENT
      - aggregated values:
          priority: 20
          original values:
            - name: SUBOPTIMAL
              operational_value: SUBOPTIMAL
      - aggregated values:
          priority: 10
          original values:
            - name: AVAILABLE
              operational_value: OK
            - name: IN-USE
              operational_value: OK
