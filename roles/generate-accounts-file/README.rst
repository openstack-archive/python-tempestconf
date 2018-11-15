Generate accounts.yaml file for tempest
=======================================

Installs tempest cloned from git and generates accounts.yaml file.
accounts.yaml file will be saved inside the cloned folder in etc/ subfolder.

The tempest configuration file, which is needed to generate tempest
accounts.yaml file will be copied into etc/ as well, however it will be
renamed to tempest_admin.conf so that, it doesn't conflict with tempest.conf
which may be there.


**Role Variables**

.. zuul:rolevar:: tempest_account_concurrency
   :default: 3

   A number of parallel test processes.

.. zuul:rolevar:: tempest_config_file
   :type: string
   :default: None
   :required: True

   A path to a tempest configuration file. It must contain credentials
   which allows to create resources.

.. zuul:rolevar:: source_credentials_commands
   :type: string
   :default: None
   :required: True

   Commands divided by a semicolon which define obtaining credentials for
   a user who has permissions to create resources. They need to be defined
   in the playbook the role is called from.
   For example for devstack it's used ({{ devstack_base_dir}} is the location
   where run-devstack role copies devstack source files):

   `source {{ devstack_base_dir }}/devstack/openrc {{ user }} {{ user }}`

   and for packstack ({{ ansible_user_dir }} is the location where
   packstack generates rc files):

   `source {{ ansible_user_dir }}/keystonerc_{{ user }}`

.. zuul:rolevar:: virtualenvs
   :type: dict

   A dictionary of paths to virtual environments.

   .. zuul:rolevar:: tempest
      :default: ~/.virtualenvs/.tempest

      A path to the virtual environment of Tempest.

.. zuul:rolevar:: tempest_src_relative_path
   :type: string

   A relative path to Tempest project which is by default cloned to the
   Zuul home directory. Value of the variable is set in the role to that
   default path. If needed, the variable can be overridden from the
   playbook where the role is called from.

.. zuul:rolevar:: accounts_file_destination
   :type: string
   :default: None

   If the variable is defined, the newly generated accounts.yaml file
   will be copied to the directory specified by the variable.

