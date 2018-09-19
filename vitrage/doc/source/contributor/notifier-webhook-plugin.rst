=====================
Webhook Configuration
=====================

Vitrage can be configured to support webhooks for the sending of
notifications regarding raised or cleared alarms to any registered target.

Enable Webhook Notifier
-----------------------

To enable the webhook plugin, add it to the list of notifiers in
**/etc/vitrage/vitrage.conf** file:

   .. code::

    [DEFAULT]
    notifiers = webhook

Webhook API
===========

Webhooks can be added, listed and deleted from the database using the
following commands:

Add
---
To add a new webhook to the database, use the command 'vitrage webhook add'.
The fields are:

+------------------+-----------------------------------------------------------------+--------------+
| Name             | Description                                                     | Required     |
+==================+=================================================================+==============+
| url              | The webhook URL to which notifications will be sent             | Yes          |
+------------------+-----------------------------------------------------------------+--------------+
| regex_filter     | A JSON string to filter for specific events                     | No           |
+------------------+-----------------------------------------------------------------+--------------+
| headers          | A JSON string specifying additional headers to the notification | No           |
+------------------+-----------------------------------------------------------------+--------------+


Usage example::

    vitrage webhook add --url https://www.myserver.com --headers
    "{'content-type': 'application/json'}" --regex_filter "{'vitrage_type':
    '.*'}"

- If no regex filter is supplied, all notifications will be sent.
- The defaults headers are : '{'content-type': 'application/json'}'

Data is sent by the webhook notifier in the following format.

* notification: ``vitrage.alarm.activate`` or ``vitrage.alarm.deactivate``
* payload: The alarm data


::

    {
      "notification": "vitrage.alarm.activate",
      "payload": {
        "vitrage_id": "2def31e9-6d9f-4c16-b007-893caa806cd4",
        "resource": {
          "vitrage_id": "437f1f4c-ccce-40a4-ac62-1c2f1fd9f6ac",
          "name": "app-1-server-1-jz6qvznkmnif",
          "update_timestamp": "2018-01-22 10:00:34.327142+00:00",
          "vitrage_category": "RESOURCE",
          "vitrage_operational_state": "OK",
          "vitrage_type": "nova.instance",
          "project_id": "8f007e5ba0944e84baa6f2a4f2b5d03a",
          "id": "9b7d93b9-94ec-41e1-9cec-f28d4f8d702c"
        },
        "update_timestamp": "2018-01-22T10:00:34Z",
        "vitrage_category": "ALARM",
        "state": "Active",
        "vitrage_type": "vitrage",
        "vitrage_operational_severity": "WARNING",
        "name": "Instance memory performance degraded"
      }
    }


Each of the fields listed can be used to filter the data when specifying a
regex filter for the webhook.


List
----
List all webhooks currently in the DB::

    vitrage webhook list

Show
----
Show a webhook with specified id::

    vitrage webhook show <id>

ID of webhooks is decided by Vitrage and can be found using the 'list' command

Delete
------
Delete a webhook with specified id::

    vitrage webhook delete <id>

ID of webhooks is decided by Vitrage and can be found using the 'list' command