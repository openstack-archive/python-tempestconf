Generate configuration file for tempest

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

