Zabbix-Vitrage Gateway
======================

Consolidate Zabbix alerts from across multiple sites into a single "at-a-glance" console by using a custom Zabbix [alertscript](https://www.zabbix.com/documentation/3.0/manual/config/notifications/media/script).


Installation
------------

**Note:** Don't try to use zabbix with docker image to test, because ``zabbix_vitrage.py`` requires some openstack libraries (``oslo.messaging`` and ``oslo.config``).

Copy the ``zabbix_vitrage.py`` script into the Zabbix servers' ``AlertScriptsPath`` directory which is by default ``/usr/lib/zabbix/alertscripts`` and make it executable:

.. code-block:: bash

    $ wget https://raw.githubusercontent.com/openstack/vitrage/master/vitrage/datasources/zabbix/auxiliary/zabbix_vitrage.py
    $ cp zabbix_vitrage.py /usr/lib/zabbix/alertscripts/
    $ chmod 755 /usr/lib/zabbix/alertscripts/zabbix_vitrage.py

Install ``oslo.messaging`` and ``oslo.config`` to zabbix host (may require root):

.. code:: bash

    $ pip install oslo.messaging oslo.config

Zabbix web ui configuration
---------------------------

To forward zabbix events to Vitrage a new media script needs to be created and associated with a user. Follow the steps below as a Zabbix Admin user:

1. Create a new media type [Administration > Media Types > Create Media Type]

    | **Name:** Vitrage Notifications
    | **Type:** Script
    | **Script name:** zabbix_vitrage.py
    | **Script parameters**:
    |   **1st line:** {ALERT.SENDTO}
    |   **2nd line:** {ALERT.SUBJECT}
    |   **3rd line:** {ALERT.MESSAGE}


2. Modify the Media for the Admin user [Administration > Users]

    | **Type:** Vitrage Notifications
    | **Send to:** ``rabbit://rabbit_user:rabbit_pass@127.0.0.1:5672/``   <--- Vitrage message bus url
    | **When active:** 1-7,00:00-24:00
    | **Use if severity:** tick all options
    | **Status:** Enabled

    **Note:** Default ``rabbit_user/rabbit_pass`` for devstack rabbitmq is ``stackrabbit/secret``

3. Configure Action [Configuration > Actions > Create Action > Action]

    | **Name:** Forward to Vitrage
    | **Default Subject:** {TRIGGER.STATUS}

    | **Add an operation:**
    |   **Send to Users:** Admin
    |   **Send only to:** Vitrage Notifications

    | **Default Message:**
    |   host={HOST.NAME1}
    |   hostid={HOST.ID1}
    |   hostip={HOST.IP1}
    |   triggerid={TRIGGER.ID}
    |   description={TRIGGER.NAME}
    |   rawtext={TRIGGER.NAME.ORIG}
    |   expression={TRIGGER.EXPRESSION}
    |   value={TRIGGER.VALUE}
    |   priority={TRIGGER.NSEVERITY}
    |   lastchange={EVENT.DATE} {EVENT.TIME}

    | **To send events add under the Conditions tab:**
    |   (A) Maintenance status not in `maintenance`

For a full list of trigger macros see https://www.zabbix.com/documentation/3.0/manual/appendix/macros/supported_by_location

To test zabbix events and vitrage alarms, please see zabbix trigger documentation: https://www.zabbix.com/documentation/3.2/manual/config/triggers/trigger


Vitrage configuration
---------------------

1. Add zabbix to list of datasources in ``/etc/vitrage/vitrage.conf``

.. code::

    [datasources]
    types = zabbix,nova.host,nova.instance,nova.zone,static,aodh,cinder.volume,neutron.network,neutron.port,heat.stack

2. Add following section to ``/etc/vitrage/vitrage.conf``

.. code::

    [zabbix]
    url = http://<ip>/zabbix  # URL to zabbix
    password = zabbix
    user = admin
    config_file = /etc/vitrage/zabbix_conf.yaml

2. Create ``/etc/vitrage/zabbix_conf.yaml`` with this content

.. code ::

    zabbix:
    - zabbix_host: Zabbix server
      type: nova.host
      name: Zabbix server

4. Restart vitrage service in devstack/openstack

DONE
----

