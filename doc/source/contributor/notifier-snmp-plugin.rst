===============================
Vitrage Notifier plugins - SNMP
===============================

Overview
========
The Evaluator may determine that an alarm should be created, deleted or otherwise updated.

Other components are notified of such changes by the Vitrage Notifier service. Among others, Vitrage Notifier is responsible for sending snmp traps for raised and deleted deduced alarms.

This document describes the implementation of generating SNMP Traps on Vitrage alarms.

SNMP Plugin
===========
The OIDs of the SNMP traps on Vitrage alarms should correspond to the definitions in the MIB file(s) used by the relevant companies.
The traps should be sent on activation and deactivation of alarms.

In order to use the SNMP plugin:
--------------------------------
1. The default SNMP sender: ``vitrage.notifier.plugins.snmp.snmp_sender.py``, in order to use it:

 - Add to ``vitrage.conf``:

    * notifiers = snmp

    * [snmp]

      consumers = <path to consumers yaml file>
      alarm_oid_mapping = <path to alarm oid mapping yaml file>
      oid_tree = <path to tree format oid configuration yaml file>

 - ``consumers`` file should be in the following format::

         - host:
             name: <subscriber name>
             send_to: <subscriber ip>
             port: <subscriber port>
             community: <community string: for example public>

       There can be more then one host

 - ``alarm_oid_mapping`` file should be in the following format:
    For each alarm::

         <headline>:
         oid: '.<number>'
         alarm_name: <alarm name as appears in Vitrage deduced alarms>

 - ``oid_tree`` file should be in the following format::

    severity_mapping:
        <mapped severity>: <number>

    snmp_tree:
        root:
            oid: <num.num....>
            next:
                node:
                    oid: <num.num....>
                    next:
                        ...
                        next:
                            node:
                            oid: <num.num....>
                            next:
                                node:
                                    oid: <num.num....>
                                    with_values: 1
                                    next:
                                        leaf:
                                            oid: <num.num....>
                                        leaf2:
                                            oid: <num.num....>
                                        ...
                                node:
                                    oid: <num.num....>
                                    next:
                                        ...
                                        next:
                                            node
                                            oid: <num.num....>
                                            next:
                                                ALARM_OID:
                                                    oid: <no num>
                                                    next:
                                                        SEVERITY: - optional
                                                            oid: <no num>


 "with_values" defines the parameters which's values should be sent in the snmp trap. If it's value is "1" then all it's children's values will be sent in the snmp trap.

 SEVERITY is an optional parameter, if it exists then severity mapping should exist

2. Optional: for defining other SNMP sender:

 - Create a package with SNMP sender

 - New SNMP sender should inherit from abstract class: ``vitrage.vitrage.notifier.plugins.snmp.base.py``

 - Define the package in vitrage.conf under [snmp] section:

    * snmp_sender_class = <Snmp sender class location>
