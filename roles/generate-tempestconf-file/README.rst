# Generate configuration file for tempest

Installs python-tempestconf cloned from git and generates tempest.conf which
is then copied to tempest directory.

**Role Variables**

.. zuul:rolevar:: devstack_base_dir
   :type: string
   :default: /opt/stack

    The devstack base directory.

.. zuul:rolevar:: virtualenvs
   :type: dict

    A dictionary of paths to virtual environments.

   .. zuul:rolevar:: tempestconf
      :default: ~/.virtualenvs/.tempestconf

       The path to the virtual environment of python-tempestconf tool.

.. zuul:rolevar:: source_credentials_commands
   :type: string

   Commands divided by a semicolon which defines sourcing credentials for
   running python-tempestconf tool with. They need to be defined in the
   playbook the role is called from.
   For example for devstack it's used ({{ devstack_base_dir}} is the location
   where run-devstack role copies devstack source files):

   `source {{ devstack_base_dir }}/devstack/openrc {{ user }} {{ user }}`

   and for packstack:

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
   When True, a set of tasks, where generation of tempest configuration is
   intended to fail, is included. The set includes also tasks, which create
   tempest resources. After that, the generation of the tempest configuration is
   suppossed to pass.
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

   Name of credentials from clouds.yaml file, which will be used to create
   tempest resources in case, test_demo_user variable is set to True.

.. zuul:rolevar:: test_accounts_file
   :type: string
   :default: /etc/openstack/accounts.yaml

   A path to a tempest accounts file. This path will be injected to
   test_accounts_file option in auth section of tempest.conf, when
   test_demo_user is set to True.

