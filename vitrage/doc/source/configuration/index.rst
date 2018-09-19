.. _configuring:

=============================
Vitrage Configuration Options
=============================

Vitrage Sample Configuration File
=================================

Configure Vitrage by editing /etc/vitrage/vitrage.conf.

No config file is provided with the source code, it will be created during the
installation. In case where no configuration file was installed, one can be
easily created by running::

    oslo-config-generator \
        --config-file=/etc/vitrage/vitrage-config-generator.conf \
        --output-file=/etc/vitrage/vitrage.conf

The following is a sample Vitrage configuration for adaptation and use. It is
auto-generated from Vitrage when this documentation is built, and can also be
viewed in `file form <../_static/vitrage.conf.sample>`_.

.. literalinclude:: ../_static/vitrage.conf.sample
