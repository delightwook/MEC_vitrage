=====================
Mistral Configuration
=====================

Vitrage can be configured to execute Mistral (the OpenStack Workflow service)
workflows based on certain topology or alarm conditions.


Enable Mistral Workflow Execution
---------------------------------

To enable Mistral workflow execution, add mistral to the list of notifiers in
/etc/vitrage/vitrage.conf file:

   .. code::

    [DEFAULT]
    notifiers = nova,mistral


Add execute_mistral action
--------------------------

To execute a Mistral workflow under a certain condition, add an
'execute_mistral' action to a template file:

   .. code:: yaml

    - scenario:
        condition: host_down_alarm_on_host
        actions:
            action:
                action_type: execute_mistral
                properties:
                    workflow: evacuate_host      # mandatory. The name of the workflow to be executed
                    hostname: host1              # optional. A list of properties to be passed to the workflow
