=====
Usage
=====

To install ``python-tempestconf`` follow our `Installation Guide`_

.. _Installation Guide: ../install/installation.html

For a successful execution of ``python-tempestconf`` a user needs to do one
of the following:

  * source OpenStack RC file before running :command:`discover-tempest-config`
    command, see `Examples of usage with sourced credentials`_
  * use ``clouds.yaml`` file and take advantage of ``openstacksdk`` support
    and use a named cloud, see `Examples of usage with a named cloud`_

If a user doesn't use ``--create``, no resources, which require admin
credentials, are created. See `Resources`_ section.


Examples of usage with sourced credentials
------------------------------------------

**All of the examples** in this section mentioned below **use** the following
step **as a prerequisite**:

  * Source your OpenStack RC file containing the cloud credentials. Let's say
    you have an overcloud_rc file with the following content:

    .. code-block:: shell-session

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

    Then it can be sourced by:

    .. code-block:: shell-session

        $ source overcloud_rc

    .. note::
        Thanks to
        `openstacksdk <https://docs.openstack.org/openstacksdk/latest/>`_
        support, ``python-tempestconf`` is able to read cloud credentials from
        the shell environment, which means, they **don't need** to be
        explicitly passed via CLI.


Override values
+++++++++++++++

Override values can be useful when a user wants to set a key-value pair in
generated ``tempest.conf`` from one of the two following reasons:

  * ``python-tempestconf`` is **not** able to discover it and therefore set the
    desired
    key-value pair in ``tempest.conf`` by itself
  * ``python-tempestconf`` is able to discover it, but a user wants to set it
    differently

Values specified as overrides will be set to tempest.conf no matter if they
were discovered or not. If a section or a key don't exist, they will be
created.

In the following example we make the tool to print debugging information, we
set that ``tempest.conf`` will be written to ``etc/`` directory and we pass
some override values.

.. code-block:: shell-session
    :emphasize-lines: 4-6

    $ discover-tempest-config \
        --debug \
        --out etc/tempest.conf \
        auth.tempest_roles Member \
        identity.username MyOverrideUsername \
        section.key MyValue

.. note::

    Please, notice that override values are written together (only then they're
    parsed correctly) and after all other arguments (that's due to better
    readability).

The generated ``tempest.conf`` will look like:

.. code-block:: shell-session

    $ cat etc/tempest.conf
    <omitted some content>
    [auth]
    tempest_roles = Member
    <omitted some content>

    [identity]
    username = MyOverrideUsername
    <omitted some content>

    [section]
    key = value
    <omitted some content>


Prevent some key-value pairs to be set in tempest.conf
++++++++++++++++++++++++++++++++++++++++++++++++++++++

A user can define key-value pairs which are not wanted to be written to the
generated ``tempest.conf``. This can be useful in case when
``python-tempestconf`` discovers something which is not wanted by a user to
have in ``tempest.conf``. If the option is used, ``python-tempestconf`` will
make sure that the defined values are not written to tempest.conf no matter
if they were discovered or not.

.. code-block:: shell-session

    $ discover-tempest-config \
        --remove section1.key1 \
        --remove section2.key2=value \
        --remove section3.key3=value1,value2

In the following case **all** api_extensions will be removed and
``tempest.conf`` will **not contain** the api_extensions key under
volume-feature-enabled section.

.. code-block:: shell-session

    $ discover-tempest-config \
        --remove volume-feature-enabled.api_extensions

In the following case **only** NMN api extension will be removed from the
api_extensions list.

.. code-block:: shell-session

    $ discover-tempest-config \
        --remove volume-feature-enabled.api_extensions=NMN

In the following case only NMN **and** OS-EXT-IPS api extensions will be
removed.

.. code-block:: shell-session

    $ discover-tempest-config \
        --remove volume-feature-enabled.api_extensions=NMN,OS-EXT-IPS

.. note::

    ``--remove`` option will remove even values set as `overrides`_

    .. _overrides: ./usage.html#override-values

.. note::

    This argument's functionality is opposite to ``--append`` one, see
    `Append values to tempest.conf`_


Append values to tempest.conf
+++++++++++++++++++++++++++++

In a case when ``python-tempestconf`` is not able to discover some wanted
api_extensions, you can make ``python-tempestconf`` append any extensions
by using ``--append`` argument.

The following will make ``python-tempestconf`` append my_ext extension to
volume-feature-enabled.api_extensions and tag and tag-ext extensions to
network-feature-enabled.api_extensions.

.. code-block:: shell-session

    $ discover-tempest-config \
        --append volume-feature-enabled.api_extensions=my_ext \
        --append network-feature-enabled.api_extensions=tag,tag-ext

.. note::

    This argument's functionality is opposite to ``--remove`` one, see
    `Prevent some key-value pairs to be set in tempest.conf`_


Usage with tempest accounts file
++++++++++++++++++++++++++++++++

To read more about ``accounts.yaml`` file and how to generate it follow these
links:

  * `what is accounts.yaml? <https://docs.openstack.org/tempest/latest/configuration.html#pre-provisioned-credentials>`_
  * `how to generate it? <https://docs.openstack.org/tempest/latest/account_generator.html>`_

When ``--test-accounts`` argument is used, ``python-tempestconf`` will not
write any credentials to generated ``tempest.conf`` file, it will add a
**test_accounts_file** key to **auth** section with value equal to the path
provided by the ``--test-accounts`` argument. Also **use_dynamic_credentials**
under **auth** section will be set to False as
`tempest documentation <https://docs.openstack.org/tempest/latest/configuration.html#pre-provisioned-credentials>`_
suggests.

This argument can be useful when a user doesn't want to store credentials in
``tempest.conf``, f.e: the user want's to share the ``tempest.conf``.

If you already have the file created, you can run
:command:`discover-tempest-config` command with ``--test-accounts`` argument:

.. code-block:: shell-session
    :emphasize-lines: 3

    $ discover-tempest-config \
        --out etc/tempest.conf \
        --test-accounts /path/to/my/accounts.yaml

The generated ``tempest.conf`` will look like:

.. code-block:: shell-session

    $ cat etc/tempest.conf
    <omitted some content>
    [auth]
    test_accounts_file = /path/to/my/accounts.yaml
    use_dynamic_credentials = False
    <omitted some content>


non-admin argument
++++++++++++++++++

If your credentials are **non-admin ones**, which means that you are
**not allowed** to create any resources in your cloud, then please specify
``--non-admin`` argument. When this argument is used, ``python-tempestconf``
will **not create** any resources.

.. code-block:: shell-session
    :emphasize-lines: 4

    $ discover-tempest-config \
        -v \
        --debug \
        --non-admin


Examples of usage with a named cloud
------------------------------------

``python-tempestconf`` supports
`openstacksdk <https://docs.openstack.org/openstacksdk/latest/>`__
so instead of sourcing an OpenStack RC file a user can use clouds.yml file.
Location where this file should be stored and syntax which is used to define
it can be found
`here <https://docs.openstack.org/openstacksdk/latest/user/config/configuration.html>`__

Let's say there is a ``clouds.yaml`` file located in ``/etc/openstack/`` with
the following content:

.. code-block:: shell-session

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

Then if you use ``--os-cloud`` argument you can run
:command:`discover-tempest-config` **without** setting any OS_* environment
variable (for example by sourcing any OpenStack RC file).

``--os-cloud`` specifies one of the cloud names located in the ``clouds.yaml``
file.

.. code-block:: shell-session
    :emphasize-lines: 3

    $ discover-tempest-config \
        --debug \
        --os-cloud devstack

So the call from `non-admin argument`_ section would for example look like:

.. code-block:: shell-session
    :emphasize-lines: 5

    $ discover-tempest-config \
        -v \
        --debug \
        --non-admin \
        --os-cloud devstack

The call from `Usage with tempest accounts file`_ section would for example
look like:

.. code-block:: shell-session
    :emphasize-lines: 2

    $ discover-tempest-config \
        --os-cloud devstack \
        --out etc/tempest.conf \
        --test-accounts /path/to/my/accounts.yaml


Resources
---------

Without specifying ``--create`` argument, no resources which require admin
credentials are crated during the ``python-tempestconf`` execution. For the
documentation on how to use ``--create`` argument see `Admin User Guide`_

.. _Admin User Guide: ../admin/admin_usage.html

This affects these types of resources:

  * users
  * images
  * flavors

Users
+++++

For a successful execution of Tempest at least two users need to be created
(the default concurrency is 2). Therefor ``python-tempestconf`` looks for
the following two users:

  * the user who started ``python-tempestconf``
  * the alt user defined by:

    * identity.alt_username
    * identity.alt_password
    * identity.alt_project_name

    .. note::
        These values are set by default, have a look at `default values`_ which
        ``python-tempestconf`` sets to a ``tempest.conf``

        .. _default values: ./default.html

If the users are not found, they can't be created, so
:command:`discover-tempest-config` ends with an exception.


Images
++++++

Any user can create an image, therefore ``--create`` argument doesn't have to
be used in order to have created images, necessary for tempest execution, by
``python-tempestconf``.

However, when non-admin credentials are used, the created images will have
**community** visibility. It's because users without admin credentials can't
create a public image and private images are not visible for other users -
tempest tests **would fail** finding the image, because they are usually run
under a **different user.**

When admin credentials are used, the images are created as public ones.

``--image`` argument is used to specify an image which will be uploaded
to glance and used later by tempest tests for booting VMs.

The following example will upload ``/my/path/to/myImage.img`` image to glance
twice. First **compute.image_ref** will be equal to the ID of the uploaded
image. Then the image is uploaded to glance again and but
**compute.image_alt_ref** is set to that corresponding ID:

.. code-block:: shell-session

    $ discover-tempest-config \
        --os-cloud myCloud \
        --image /my/path/to/myImage.img

In the following example, an `override`_  value is used to set
**compute.image_ref**, which means that the image specified by  ``--image`` is
uploaded and only **compute.image_alt_ref** is set to the ID of newly created
image.

.. _override: ./usage.html#override-values

.. code-block:: shell-session

    $ discover-tempest-config \
        --os-cloud myCloud \
        compute.image_ref 2eb9f6c9-bd32-427d-850d-c3bb3cfaaa87

.. note::
    ``python-tempestconf`` checks by image name, if it is already present
    in glance and only in case it's not present there, will upload the
    image.

.. note::

    If the image ID specified as an override is not found, the image where
    ``--image`` points to is used.

    If ``--image`` is not defined, the default image (see `CLI options`_)
    is chosen to be uploaded.

    .. _CLI options: ../cli/cli_options.html

Converting images to .raw format
********************************

By using ``--convert-to-raw`` argument you can make ``python-tempestconf``
convert the image given by ``--image`` argument to **.raw** format before
uploading it to glance. If Ceph is used as a backend, the boot time of the
image will be faster when the image is already in **.raw** format.

In the following example the ``/my/path/to/myImage.img`` image will be
downloaded, then converted to **.raw** format and then uploaded to glance.

.. code-block:: shell-session

    $ discover-tempest-config \
        --os-cloud myCloud \
        --image /my/path/to/myImage.img \
        --convert-to-raw


Flavors
+++++++

``python-tempestconf`` looks by default for these two flavors:

  * *m1.nano* with 64 MB of RAM, which will be set as **compute.flavor_ref**
  * *m1.micro* with 128 MB of RAM, which will be set as
    **compute.flavor_alt_ref**

If a user used ``--flavor-min-mem`` argument, ``python-tempestconf`` will look
for these two flavors:

  * *custom*
  * *custom_alt*

    .. note::

        ``python-tempestconf`` looks for flavors by name, so if a user has had
        a flavor with name *custom*/*custom_alt* already created, those flavors'
        IDs will be set as **compute.flavor_ref**/**compute.flavor_ref_alt**
        without checking if theirs RAM size is equal to the one specified by
        ``--flavor-min-mem``.

If they are not found and ``--create`` argument is not used, the tool will try
to auto discover two smallest flavors available in the system. If at least two
flavors are not found, the tool ends with an exception.

If two flavors are found, their IDs will be set to ``tempest.conf``, see the
following example:

.. code-block:: shell-session

    $ discover-tempest-config \
        --out etc/tempest.conf

The generated tempest.conf will look like:

.. code-block:: ini

    $ cat etc/tempest.conf
    <omitted some content>
    [compute]
    # typically an ID of the smaller flavor found
    flavor_ref = <ID_1>
    # typically an ID of the bigger flavor found
    flavor_alt_ref = <ID_2>
    <omitted some content>

In the following example, an `override`_ option specifies **compute.flavor_ref**
ID, which if it's found, the tool continues with looking for a **m1.micro**
flavor to be set as **compute.flavor_alt_ref** as was explained above.

.. code-block:: shell-session

    $ discover-tempest-config \
        --out etc/tempest.conf \
        compute.flavor_ref 123

.. note::
    If the **compute.flavor_ref** ID is not found, the tool ends with an
    exception.
