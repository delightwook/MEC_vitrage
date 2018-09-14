===========================
Nagios Plugin Configuration
===========================

Configure Access to Nagios
--------------------------

The following should be set in ``/etc/vitrage/vitrage.conf``, under ``[nagios]`` section:

+------------------+---------------------------------------------------------+-------------------------------+
| Name             | Description                                             | Default Value                 |
+==================+=========================================================+===============================+
| user             | Nagios user                                             |                               |
+------------------+---------------------------------------------------------+-------------------------------+
| password         | Nagios password                                         |                               |
+------------------+---------------------------------------------------------+-------------------------------+
| url              | Nagios url for querying the data                        |                               |
+------------------+---------------------------------------------------------+-------------------------------+
| config_file      | Nagios configuration file                               | /etc/vitrage/nagios_conf.yaml |
+------------------+---------------------------------------------------------+-------------------------------+
| changes_interval | Interval of checking changes in the configuration files | 30 seconds                    |
+------------------+---------------------------------------------------------+-------------------------------+

**Note:** To avoid issues with paging, it is recommended for the URL to be of
the form *http://<nagios site url>/cgi-bin/status.cgi*, which returns all the
nagios tests.

Nagios access configuration - example
+++++++++++++++++++++++++++++++++++++

When installing Nagios on devstack with IP 10.20.30.40, following
the instructions here_, this would be the correct configuration:

.. _here: nagios-devstack-installation.html

.. code::

  [nagios]
  user = omdadmin
  password = omd
  url = http://10.20.30.40:54321/my_site/nagios/cgi-bin/status.cgi
  config_file = /etc/vitrage/nagios_conf.yaml

Configure Nagios Host Mapping
-----------------------------

Nagios tests are defined in a table with columns: Host, Service, Status, Last
Check, etc.

A Nagios "host" is not necessarily a resource of type "nova.host". It can also
be an instance, switch, or other resource types. **nagios_conf.yaml** is used
to map each Nagios host to a Vitrage resource.

Format
++++++

.. code ::

 nagios:
  - nagios_host: <Host as appears in Nagios>
    type: <resource type in Vitrage>
    name: <resource name in Vitrage>

  - nagios_host: <Host as appears in Nagios>
    type: <resource type in Vitrage>
    name: <resource name in Vitrage>
  ...

Note that for ease of use, there is support for wildcards in the "nagios_host"
value, and references to the actual value for a given wildcard match. See
**Example 2** below.



Example 1
+++++++++

The following example is for a system with two hosts. In nagios they are named
*compute-0, compute-1*, and in nova they are named *host-1, host-2*.

.. code::

 nagios:
  - nagios_host: compute-0
    type: nova.host
    name: host1

  - nagios_host: compute-1
    type: nova.host
    name: host2

Example 2
+++++++++

The following file will
 - map all Nagios hosts named ``host-<some_suffix>`` or ``<some_prefix>-devstack``
   to resources of type ``nova.host`` with the same name.
 - map all Nagios hosts named ``instance-<some_suffix>`` to ``nova.instance``
   resources.

Note how the ``${nagios_host}`` references the instantiation of the regex defined
in ``nagios_host``.

.. code::

 nagios:
  - nagios_host: host-(.*)
    type: nova.host
    name: ${nagios_host}

  - nagios_host: (.*)-devstack
    type: nova.host
    name: ${nagios_host}

  - nagios_host: instance-(.*)
    type: nova.instance
    name: ${nagios_host}

