Nagios-for-Devstack Configuration Guide
=======================================

Overview
--------

This page describes how to manually install and configure Nagios on devstack.
After following the steps described here, Nagios will be installed via the OMD
package (http://omdistro.org/) and will have a basic set of tests for
monitoring the Devstack VM. It will then be possible to configure a Nagios
datasource for Vitrage.

The following guide is for Ubuntu. With slight modifications it should work for
other linux flavours. Links for this purpose are added below.


Prerequisites
-------------
Install devstack with vitrage before install Nagios via OMD due to this issue_

.. _issue: https://bugs.launchpad.net/vitrage/+bug/1629811


Installation
------------

1. Update your repo to include the OMD key:

   .. code::

    wget -q "https://labs.consol.de/repo/stable/RPM-GPG-KEY" -O - | sudo apt-key add -

2. Update your repo with the OMD site. For example, for ubuntu trusty release:

   .. code::

    sudo bash -c "echo 'deb https://labs.consol.de/repo/stable/ubuntu trusty main' >> /etc/apt/sources.list"
    sudo apt-get update

 For additional distros, see https://labs.consol.de/repo/stable/

3. Install OMD

   .. code::

    sudo apt-get install omd

4. Create a site for nagios with a name of your choosing, for example
   ``my_site``.

   .. code::

    sudo omd create my_site
    sudo omd config my_site set APACHE_TCP_PORT 54321
    sudo omd config my_site set APACHE_TCP_ADDR 0.0.0.0
    sudo omd start  my_site

   You can now access your Nagios site here: *http://<devstack_ip>:54321/my_site/omd/*.

   .. code::

    username: omdadmin
    password: omd

  *Notes:*
    - The default port is OMD uses is 5000, which is also used by OpenStack
      Keystone, and so it must be changed. Port 54321 used here is only an
      example.
    - *APACHE_TCP_ADDR* indicates the address to listen on. Use 0.0.0.0 to
      listen for all traffic addressed to the specified port. Use a different
      address to listen on a specific (public) address.
    - When using devstack, remember to stop omd apache2's sites

5. Install the Check_MK agent on devstack VM:

   .. code::

    sudo apt-get install check-mk-agent

6. Activate the Check_MK agent, by editing ``/etc/xinetd.d/check_mk`` and
   **setting "disable" to "no"**, and then run

   .. code::

    sudo service xinetd restart

7. In your browser, go to *http://<devstack_ip>:<selected port>/my_site/omd/*
   and follow the instructions at this link_ (**"Configuring the first host and
   checks"** section) to configure the nagios host.

   .. _link: http://mathias-kettner.de/checkmk_install_with_omd.html#H1:Configuring_the_first_host_and_checks

8. *Vitrage Support.* With Nagios installed, you can now configure a datasource
   for it for Vitrage, by following the instructions here_.

   .. _here: nagios-config.html
