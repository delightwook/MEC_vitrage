====================================
Root Cause Analysis service overview
====================================

Vitrage provides a root cause analysis service, which is used for analyzing the topology and alarms of the cloud, and providing insights about it.

The Root Cause Analysis service consists of the following components:

``vitrage-graph`` service
  The main process. It includes the in-memory entity graph and the template evaluator.
``vitrage-notifier`` service
  Used for notifying external systems about Vitrage alarms/state changes. It only calls Nova force-down API
  and Simple Network Management Protocol (SNMP) in the Ocata release.
``vitrage-api`` service
  The API layer for Vitrage.
``vitrage-collector`` service
  Responsible for retrieving data from the different datasources.
``vitrage-ml`` service
  Performs alarm analysis using Machine Learning methods.
``vitrage-persistor`` service
  Used to persist the events coming from the datasources in a database.
