==================
Configure Keycloak
==================

Overview
========

`Keycloak`_, is an open source Identity and Access Management solution aimed at modern applications and services.
It can be used as an authentication service instead of keystone.

.. _Keycloak: http://www.keycloak.org

Configuration
=============

Keycloak must be enabled **explicitly** in Vitrage configuration file
The default authentication mode is keystone::

    [api]
    auth_mode = keycloak

    [keycloak]
    auth_url = http://<Keycloak-server-host>:<Keycloak-server-port>/auth
    insecure = False


- ``auth_url`` url of the Keycloak server defaults to ``http://127.0.0.1:9080/auth``
- ``insecure`` If True, SSL/TLS certificate verification is disabled defaults to ``False``