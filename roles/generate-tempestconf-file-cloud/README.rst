Generate configuration file for tempest from cloud credentials

Installs python-tempestconf cloned from git and generates tempest.conf with
credentials saved in clouds.yaml file. The tempest configuration file is printed
to the output.

**Role Variables**

.. zuul:rolevar:: cloud_user
   :type: string
   :default: devstack

   Named cloud with demo user credentials as a default value.

.. zuul:rolevar:: virtualenvs
   :type: dict

    A dictionary of paths to virtual environments.

   .. zuul:rolevar:: tempestconf
      :default: ~/.virtualenvs/.tempestconf

       The path to the virtual environment of python-tempestconf tool.

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
