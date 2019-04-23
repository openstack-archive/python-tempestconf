=====
Usage
=====

**Before** reading this page, **it's recommended** to go through `User Guide`_
first as the content on this site is more advanced and uses knowledge gained
from the `User Guide`_.

.. _User Guide: ../user/usage.html

This page shows examples of usage of ``python-tempestconf`` where **admin
credentials** are **required**. That means, only users with admin credentials
will run :command:`discover-tempest-config` with arguments described on this
page successfully.

Why admin credentials? It's because ``python-tempestconf`` can create resources
**necessary** for tempest execution in order to make user's life easier.

The following resources are created **only when** ``--create`` argument is
used:

  * flavors, to see what flavors are created, see User Guide, `Flavors`_
    section
  * users, to see what users are created, see User Guide, `Users`_ section

  .. _Flavors: ../user/usage.html#flavors
  .. _Users: ../user/usage.html#users


Examples
--------

In the following example, ``python-tempestconf`` will create all necessary
resources (`Flavors`_ and `Users`_) if they don't exist already:

.. code-block:: shell-session

    $ discover-tempest-config \
        --os-cloud devstack-admin \
        --create

If a user wants to use a custom image (instead of the default cirros one),
a minimum memory and disk size for new flavors can be defined by
``--flavor-min-mem`` and ``--flavor-min-disk`` arguments.

.. code-block:: shell-session

    $ discover-tempest-config \
        --image <path/url to custom image> \
        --flavor-min-mem 1024 \
        --flavor-min-disk 10

In the example above ``python-tempestconf`` will create *custom* flavor with
1024 MB of RAM and 10 GB of disk size and *custom_alt** flavor with 1024 + 1 MB
of RAM and 10 GB of disk size.


``python-tempestconf`` can also create a minimal accounts file when
``--create-accounts-file`` is used. It can be useful when a user doesn't have
any ``accounts.yaml`` and wants to create it. It can be done with one call:

.. code-block:: shell-session

    $ discover-tempest-config \
        --os-cloud devstack-admin \
        --create \
        --create-accounts-file ~/accounts.yaml

The call above will behave the same as if ``--test-accounts`` argument was
used, `see here`_. The generated accounts file will look similarly to this one:

.. _see here: ../user/usage.html#usage-with-tempest-accounts-file

.. code-block:: ini

    $ cat ~/accounts.yaml
    # A minimal accounts.yaml file
    # Will likely not work with swift, since additional
    # roles are required. For more documentation see:
    # https://opendev.org/openstack/tempest/src/branch/master/etc/accounts.yaml.sample

    - password: password
      project_name: admin
      username: admin

.. note::
    More about accounts file can be found in our documentation about
    `Usage with tempest accounts file`_

    .. _Usage with tempest accounts file: ../user/usage.html#usage-with-tempest-accounts-file



