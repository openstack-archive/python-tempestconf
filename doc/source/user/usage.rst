========
Usage
========


To install python-tempestconf follow `Installation Guide`_

.. _Installation Guide: ../install/installation.html


1. Source cloud credentials, for example:

.. code-block:: shell-session

    $ source cloudrc

2. Run python-tempestconf to generate tempest configuration file:

.. code-block:: shell-session

    $ discover-tempest-config --debug --create

After this, ``./etc/tempest.conf`` is generated.

.. note::
   In Ocata release new features were presented.
   ``discover-tempest-config`` is the new name of the **old**
   ``config_tempest.py`` script and it **accepts the same parameters.**
   More about new features can be found
   `here <https://blogs.rdoproject.org/2017/02/testing-rdo-with-tempest-new-features-in-ocata/>`__


os-client-config support
------------------------

python-tempestconf supports `os-client-config <https://git.openstack.org/openstack/os-client-config>`__
so instead of sourcing openstackrc files you can use clouds.yml files. Location where
these files should be stored and syntax which is used to specify cloud.yaml files
can be found `here <https://docs.openstack.org/os-client-config/latest/user/configuration.html#config-files>`__

.. code-block:: shell-session

    $ discover-tempest-config --debug --create --os-cloud <name of cloud>

