===============================================
Use python-tempestconf with a profile.yaml file
===============================================

A ``profile.yaml`` is helpful mainly in jobs running on different versions of
OpenStack, because arguments for ``python-tempestconf`` may differ in each
OpenStack version. Using the ``--profile`` argument those jobs can use
a ``profile.yaml`` file for each OpenStack version which makes the code of
those jobs much clearer and more readable, as for example they contain less if
else statements, ...

.. note::

    Apart from ``--deployer-input`` config file which specifies content of
    a tempest.conf, ``profile.yaml`` file defines arguments which are passed
    to ``python-tempestconf``, see `CLI documentation`_.

    .. _CLI documentation: ../cli/cli_options.html

.. warning::

    If this argument is used, other arguments cannot be defined, it means,
    user uses either CLI arguments or profile.yaml file.

Generating a sample profile.yaml file
+++++++++++++++++++++++++++++++++++++

.. code-block:: Bash

    $ discover-tempest-config --generate-profile ./etc/profile.yaml

.. code-block:: yaml

    $ cat ./etc/profile.yaml
    collect_timing: false
    create: false
    create_accounts_file: null
    debug: false
    deployer_input: null
    endpoint_type: null
    generate_profile: ./etc/profile.yaml
    http_timeout: null
    image: http://download.cirros-cloud.net/0.3.5/cirros-0.3.5-x86_64-disk.img
    image_disk_format: qcow2
    insecure: false
    network_id: null
    no_default_deployer: false
    non_admin: false
    os_api_version: null
    os_auth_type: password
    os_auth_url: null
    os_cacert: null
    os_cert: null
    os_cloud: null
    os_default_domain_id: null
    os_default_domain_name: null
    os_domain_id: null
    os_domain_name: null
    os_endpoint_override: null
    os_endpoint_type: null
    os_interface: public
    os_key: null
    os_password: null
    os_project_domain_id: null
    os_project_domain_name: null
    os_project_id: null
    os_project_name: null
    os_region_name: null
    os_service_name: null
    os_service_type: null
    os_system_scope: null
    os_trust_id: null
    os_user_domain_id: null
    os_user_domain_name: null
    os_user_id: null
    os_username: null
    out: etc/tempest.conf
    test_accounts: null
    timeout: 600
    verbose: false
    append: {}
      #identity.username: username
      #network-feature-enabled.api_extensions:
      #  - dvr
      #  - extension
    overrides: {}
      #identity.username: username
      #identity.password:
      #  - my_password
      #network-feature-enabled.api_extensions:
      #  - dvr
      #  - extension
    remove: {}
      #identity.username: username
      #network-feature-enabled.api_extensions:
      #  - dvr
      #  - extension

.. note::

    The generated sample of a ``profile.yaml`` file contains all
    ``python-tempestconf`` arguments set to their default values. That means,
    that you can **remove arguments you didn't modify** to keep the file simple
    and more readable.


``python-tempestconf`` accepts both of the following inputs, so you can use
what suits you better, either strings or lists:

.. code-block:: yaml

    create: True
    out: ./etc/tempest.conf
    deployer-input: ./deploy.txt
    no-default-deployer: False
    overrides:
      identity.username: my_override
      identity.password: my_password
      network-feature-enabled.api_extensions: all
      volume-feature-enabled.api_extensions: dvr,mine
    remove:
      auth.identity: username
      network-feature-enabled.api_extensions: ''
      volume-feature-enabled.api_extensions: dvr,mine


.. code-block:: yaml

    create: True
    out: ./etc/tempest.conf
    deployer-input: ./deploy.txt
    no-default-deployer: False
    overrides:
      identity.username: my_override
      identity.password:
        - my_password
      network-feature-enabled.api_extensions:
        - all
      volume-feature-enabled.api_extensions:
        - dvr
        - mine
    remove:
      auth.identity: username
      network-feature-enabled.api_extensions:
        - ''
      volume-feature-enabled.api_extensions:
        - dvr
        - mine


Using profile.yaml file
+++++++++++++++++++++++

After you've created your customized ``profile.yaml`` file, let's say in
``./etc/profile.yaml``, use it as follows:

.. code-block:: Bash

    $ discover-tempest-config --profile ./etc/profile.yaml
