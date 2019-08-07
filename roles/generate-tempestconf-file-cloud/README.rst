Generate configuration file for tempest from cloud credentials
==============================================================

Installs python-tempestconf cloned from git and generates tempest.conf with
credentials saved in clouds.yaml file. The tempest configuration file is printed
to the output after that.

**Role Variables**

.. zuul:rolevar:: branch
   :type: string
   :default: master

   Branch name upper-constraints will be taken into account from when
   python-tempestconf is installed in a venv.

.. zuul:rolevar:: cloud_user
   :type: string
   :default: devstack

   Named cloud with demo user credentials as a default value.

.. zuul:rolevar:: virtualenvs
   :type: dict

   A dictionary of paths to virtual environments.

   .. zuul:rolevar:: tempestconf
      :default: ~/.virtualenvs/.tempestconf

      A path to the virtual environment of python-tempestconf tool.

.. zuul:rolevar:: tempestconf_src_relative_path
   :type: string

   A relative path to a python-tempestconf project which is by default cloned
   to the Zuul home directory. Value of the variable is set in the role to
   that default path. If needed, the variable can be overridden from the
   playbook where the role is called from.
