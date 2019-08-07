Generate configuration file for tempest
=======================================

Installs python-tempestconf cloned from git and generates tempest.conf which
is then copied to tempest directory.

**Role Variables**

.. zuul:rolevar:: branch
   :type: string
   :default: None

   Branch name upper-constraints will be taken into accounts from when
   python-tempestconf is installed in a venv.

.. zuul:rolevar:: devstack_base_dir
   :type: string
   :default: /opt/stack

   The devstack base directory.

.. zuul:rolevar:: virtualenvs
   :type: dict

   A dictionary of paths to virtual environments.

   .. zuul:rolevar:: tempestconf
      :default: ~/.virtualenvs/.tempestconf

      A path to the virtual environment of python-tempestconf tool.

.. zuul:rolevar:: source_credentials_commands
   :type: string
   :required: True

   Commands divided by a semicolon which define obtaining credentials for
   running python-tempestconf tool with. They need to be defined in the
   playbook the role is called from.
   For example for devstack it's used ({{ devstack_base_dir}} is the location
   where run-devstack role copies devstack source files):

   `source {{ devstack_base_dir }}/devstack/openrc {{ user }} {{ user }}`

   and for packstack ({{ ansible_user_dir }} is the location where
   packstack generates rc files):

   `source {{ ansible_user_dir }}/keystonerc_{{ user }}`

.. zuul:rolevar:: url_cirros_image
   :type: string
   :default: http://download.cirros-cloud.net/0.3.5/cirros-0.3.5-x86_64-disk.img

   A URL address of the cirros image.

.. zuul:rolevar:: tempestconf_src_relative_path
   :type: string

   A relative path to a python-tempestconf project which is by default cloned
   to the Zuul home directory. Value of the variable is set in the role to
   that default path. If needed, the variable can be overridden from the
   playbook where the role is called.


.. zuul:rolevar:: aditional_tempestconf_params
   :type: string
   :default: ""

   Additional parameters for tempestconf if more specific parameters are
   needed, different from the ones which are the same for devstack and tempest.

.. zuul:rolevar:: test_demo_user
   :type: Boolean
   :default: False

   If checking of demo user abilities is desired to be enabled, set this
   variable to True.
   When True, a set of tasks for testing demo user is included. The set
   includes tasks, which create necessary tempest resources.
   NOTE: If the variable is set to True, it's needed to set cloud_admin variable
   as well, see info below.

.. zuul:rolevar:: output_path
   :type: string
   :default: None

   If the variable is defined, the newly generated tempest.conf will be saved
   accordingly.
   Example:
   output_path: /etc/openstack/tempest.conf
   Result:
   The generated tempest.conf file will be saved as /etc/openstack/tempest.conf

.. zuul:rolevar:: cloud_admin
   :type: string
   :default: None
   :required: required if test_demo_user == True

   Name of credentials from clouds.yaml file, which will be used to create
   tempest resources in case, test_demo_user variable is set to True.

.. zuul:rolevar:: test_accounts_file
   :type: string
   :default: /etc/openstack/accounts.yaml

   A path to a tempest accounts file. This path will be injected to
   test_accounts_file option in auth section of tempest.conf, when
   test_demo_user is set to True.

.. zuul:rolevar:: create_accounts_file
   :type: Boolean
   :default: False

   If True and demo user is used a minimal accounts.yaml file will be generated
   and used during tempest testing.

