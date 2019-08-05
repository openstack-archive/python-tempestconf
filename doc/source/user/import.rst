=======================================
Use python-tempestconf as Python module
=======================================

``python-tempestconf`` can be imported and used from a different Python project.

.. warning::

    The import of config_tempest is possible **only when the version of the
    tool is at least 2.0.0**.

Installation
++++++++++++

See our `Install Guide`_ on how to install ``python-tempestconf``.

.. _Install Guide: ../install/installation.html

Import
++++++

Import ``python-tempestconf`` in your project as follows:

.. code-block:: Python

    from config_tempest import main as tempestconf

``python-tempestconf`` needs cloud credentials in order to create a tempest
configuration file. There is a helper method for obtaining cloud credentials
which uses
`openstacksdk <https://docs.openstack.org/openstacksdk/latest/user/config/configuration.html>`_
for parsing the cloud for credentials.

The following example shows how to get cloud credentials and how to pass it to
the configuration tool:

.. code-block:: Python

    # The following call will return a dict containing cloud credentials,
    # for example:
    # >>> tempestconf.get_cloud_creds(args_namespace)
    # {
    #     'username': 'demo',
    #     'project_name': 'demo',
    #     'user_domain_name': 'Default',
    #     'auth_url': 'http://172.16.52.8:5000/v3',
    #     'password': 'f0921edc3c2b4fc8',
    #     'project_domain_name': 'Default'
    # }
    cloud_creds = tempestconf.get_cloud_creds(args_namespace)

    # Then the configuration step can be run using:
    tempestconf.config_tempest(cloud_creds=cloud_creds)

.. note::

    If `args_namespace` contains ``--os-cloud`` argument, the `get_cloud_creds`
    method returns cloud credentials related to that cloud, otherwise, it
    returns credentials of the current cloud (according to the sourced
    credentials).


List of arguments which may be passed to `config_tempest`
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++

 * cloud_creds
 * create
 * create_accounts_file
 * debug
 * deployer_input
 * image_disk_format
 * image_path
 * network_id
 * non_admin
 * os_cloud
 * out
 * overrides
 * remove
 * test_accounts
 * verbose

 OR

 * profile, see why **or** in `CLI documentation`_

.. note::

    For detailed description of the options see our `CLI documentation`_

    .. _CLI documentation: ../cli/cli_options.html


Example implementation
++++++++++++++++++++++

1. Save following code snippet as ``example.py``:

    .. code-block:: Python

        import argparse
        from config_tempest import main as tempestconf

        parser = argparse.ArgumentParser(description='Example implementation.')
        args = parser.parse_args()

        # get the credentials of the current cloud according to
        # the sourced credentials
        cloud_creds = tempestconf.get_cloud_creds(args)

        tempestconf.config_tempest(non_admin=True,
                                   out='./etc/tempest.conf',
                                   cloud_creds=cloud_creds)

2. Source your OpenStack RC file containing the cloud credentials. Let's say
   you have a overcloud_rc file with the following content:

    .. code-block:: Bash

        $ cat overcloud_rc
        unset OS_SERVICE_TOKEN
        export OS_USERNAME=demo
        export OS_PASSWORD='password'
        export OS_AUTH_URL=http://172.16.52.15/identity/v3
        export PS1='[\u@\h \W(keystone_demo)]\$ '
        export OS_PROJECT_NAME=demo
        export OS_USER_DOMAIN_NAME=default
        export OS_PROJECT_DOMAIN_NAME=default
        export OS_IDENTITY_API_VERSION=3

   Then it can be source by:

    .. code-block:: Bash

        $ source overcloud_rc


3. Run ``example.py``:

    .. code-block:: Bash

        $ python example.py


Example implementation with a named cloud
+++++++++++++++++++++++++++++++++++++++++

1. Let's say there is a ``clouds.yaml`` file located in ``/etc/openstack/``
   with the following content:

    .. code-block:: Bash

        $ cat /etc/openstack/clouds.yaml
        clouds:
          devstack:
            auth:
              auth_url: http://172.16.52.15/identity/v3
              password: password
              project_domain_id: default
              project_name: demo
              user_domain_id: default
              username: demo
            identity_api_version: '3'
            region_name: RegionOne
            volume_api_version: '2'


2. Save following code snippet as ``example.py``:

    .. code-block:: Python

        import argparse
        from config_tempest import main as tempestconf

        parser = argparse.ArgumentParser(description='Example implementation.')
        # Let's add an os_cloud option which will be passed
        # to config_tempest later.
        parser.add_argument('--os-cloud', help='Name of a named cloud.')
        args = parser.parse_args()

        # get the credentials to the devstack cloud
        cloud_creds = tempestconf.get_cloud_creds(args)

        tempestconf.config_tempest(non_admin=True,
                                   out='./etc/tempest.conf',
                                   cloud_creds=cloud_creds)

3. Run ``example.py``:

    .. code-block:: Bash

        $ python example.py --os-cloud devstack

    .. note::

        In this example you **don't need** to source cloud credentials. The
        credentials are obtained from the ``/etc/openstack/clouds.yaml`` file
        thanks to ``--os-cloud`` argument.
