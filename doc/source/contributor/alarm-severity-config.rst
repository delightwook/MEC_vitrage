============================
Alarm Severity Configuration
============================

Overview
--------

Vitrage retrieves information from diverse data-sources regarding alarms in
the cloud, and stores and combines this information into a unified system
model. An important property of an alarm is its **severity**. This severity can
be used both in the Vitrage templates to trigger actions, and in the Horizon UI
for color-coding purposes. Therefore, it is important that within the Vitrage
data model, severity names are aggregated and normalized.

Since each data-source might represent severity differently, for each
data-source we can supply it's own mapping to the aggregated severity supported
in Vitrage. This way we can know which severity is more important.
In addition we also normalize the severities for the horizon UI (called
``vitrage_operational_severity``) in order for the UI to know what color to show in
Horizon.

This page explains how to handle this mapping for a given
data-source.


Configure Access to Alarm Severity
----------------------------------

The alarm severity configuration is handled via config files. The location of
these files can be determined in **/etc/vitrage/vitrage.conf**. Under the
[entity_graph] section, set:

+------------------------+------------------------------------+----------------------------------+
| Name                   | Description                        | Default Value                    |
+========================+====================================+==================================+
| datasources_values_dir | Directory path from where to load  | /etc/vitrage/datasources_values/ |
|                        | the values configurations          |                                  |
+------------------------+------------------------------------+----------------------------------+


Configure Alarm Severity Mapping
--------------------------------

The alarm severity configuration files configure how the severity of each
alarm is aggregated and normalized. There are several guidelines for creating
a config file:

- Severity comes with a priority, the higher severity "wins" in case
  the same deduced alarm is raised in two scenarios (e.g., a host alarm caused
  by both memory low and cpu high)
- Operational severity is a normalized severity values can be mapped to
  specific defined values which can be found in operational_alarm_severity.py
  (OperationalAlarmSeverity class).
- Aggregated severity is not used at the moment. It is designed for the use case
  that an alarm is given different severities from different sources (e.g., a
  host alarm raised both by nagios and Vitrage), the severity with the highest
  priority will be used as the **aggregated severity**.
- The config file is in YAML format.
- The config filename must be <datasource name>.yaml, for the relevant
  datasource.
- Defining a config file for each datasource is recommended, but not mandatory.
  Datasources with no such configuration will use the values as-is.

Once the file is modified, you must restart **vitrage-graph** service to load
the changes.

Default Configuration
+++++++++++++++++++++

Default configurations for alarms severities will be installed with Vitrage for
all the pre-packaged data-sources.

Format
++++++

.. code:: yaml

    category: ALARM
    values:
      - aggregated values:
          priority: <Alarm severity priority - an integer>
          original values:
            - name: <Original alarm severity name>
              operational_value: <normalized alarm severity - from OperationalAlarmSeverity class>
            - name: ... # can list several severities for one aggregation
      - aggregated values:
          priority: ... # can list several aggregated severities
          ...
  ...


Example
+++++++

The following file will map alarm severities.

For aggregated severity with priority 40 we have 2 severities and each one of
them is mapped to operational severity CRITICAL.

For aggregated severity with priority 30 we have 1 severity called WARNING and
it is mapped to operational severity WARNING, etc...

.. code:: yaml

    category: ALARM
    values:
      - aggregated values:
          priority: 40
          original values:
            - name: CRITICAL
              operational_value: CRITICAL
            - name: DOWN
              operational_value: CRITICAL
      - aggregated values:
          priority: 30
          original values:
            - name: WARNING
              operational_value: WARNING
      - aggregated values:
          priority: 20
          original values:
            - name: UNKNOWN
              operational_value: N/A
      - aggregated values:
          priority: 10
          original values:
            - name: OK
              operational_value: OK
            - name: UP
              operational_value: OK
