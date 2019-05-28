Install tempest plugins
=======================

The role installs tempest plugins via tox inside venv-tempest virtual
environment.

**Role variables**

.. zuul:rolevar:: plugins_paths
   :type: list

   A list of paths to tempest plugins which will be installed together with
   Tempest (in the same virtual environment).

.. zuul:rolevar:: devstack_base_dir
   :type: string
   :default: /opt/stack

   The devstack base directory.
