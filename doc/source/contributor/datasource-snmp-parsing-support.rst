===========================================
Adding Snmp Parsing Support in A Datasource
===========================================

Overview
--------
Vitrage provides a service to parse snmp traps and send the parsed
event to RabbitMQ queue. To add the snmp trap to graph, there should be
a datasource that gets the event and processes it.

HOW to support Snmp Parsing Service in a datasource
---------------------------------------------------
In order to extend snmp support in datasources and configure it, users
need to do the following:

 1. Add the snmp configuration file ``snmp_parsing_conf.yaml``. It configures
    the oid that maps system information and event type when snmp parsing service
    sends message.

    **Example**

    .. code:: python

        - system_oid: 1.3.6.1.4.1.3902.4101.1.3.1.12
          system: iaas_platform
          event_type: vitrage.snmp.event

 2. Under snmp_parsing package ``__init__.py``, set ``oid_mapping`` property
    to the path of snmp configuration file.

 3. In the driver class of your alarm datasource package, add an event type in the method
    ``get_event_types``, which can be ``vitrage.snmp.event`` according to the config file
    above.

 4. To transform parsed snmp trap to standard alarm event, need to add mapping of oid and
    alarm property. Take mapping of oids and doctor event properties as an example.

    **Example**

    .. code:: python

        OID_INFO = [('1.3.6.1.6.3.1.1.4.1.0', 'status'),
                    ('1.3.6.1.4.1.3902.4101.1.3.1.4', 'hostname'),
                    ('1.3.6.1.4.1.3902.4101.1.3.1.5', 'source'),
                    ('1.3.6.1.4.1.3902.4101.1.3.1.6', 'cause'),
                    ('1.3.6.1.4.1.3902.4101.1.3.1.7', 'severity'),
                    ('1.3.6.1.4.1.3902.4101.1.3.1.8', 'monitor_id'),
                    ('1.3.6.1.4.1.3902.4101.1.3.1.9', 'monitor_event_id'),
                    ('1.3.6.1.4.1.3902.4101.1.3.1.12', 'system')]

    The value of key '1.3.6.1.6.3.1.1.4.1.0' defines snmp trap's report or recover status,
    and it's also an oid. There should be a mapping of this relationship.

    **Example**

    .. code:: python

        ALARM_STATUS = {'1.3.6.1.4.1.3902.4101.1.4.1.1': 'up',
                        '1.3.6.1.4.1.3902.4101.1.4.1.2': 'down'}


 5. The method ``enrich_event`` of the driver class is responsible for enriching given event.
    The following code should be added at the beginning of ``enrich_event``. Note that the event
    type ``vitrage.snmp.event`` here is consistent with the example of config file above.

    **Example**

    .. code:: python

        if 'vitrage.snmp.event' == event_type:
            self._transform_snmp_event(event)

    The function ``_transform_snmp_event`` transform a parsed snmp trap to event of standard
    format. An example is as follows. ``self.OID_INFO`` and ``self.ALARM_STATUS`` are defined
    in the example above, and their content depends on SNMP trap organization.

    **Example**

    .. code:: python

        def _transform_snmp_event(self, event):
            src_details = event['details']
            event_details = {}

            for (oid, field_name) in self.OID_INFO:
                if oid not in src_details.keys():
                    continue
                event_details[field_name] = self._get_oid_mapping_value(field_name, src_details[oid])
            event['details'] = event_details

        def _get_oid_mapping_value(self, field_name, value):
            if field_name == 'status':
                value = extract_field_value(self.ALARM_STATUS, value)
            return value
