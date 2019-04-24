=================
How to Contribute
=================

``python-tempestconf`` source code is publicly available. You can contribute
code to individual projects, documentation, report bugs and vulnerabilities and
request features.


Reporting Bugs
--------------

We have a `storyboard project <https://storyboard.openstack.org/#!/project/912>`_
created to track any change required for ``python-tempestconf``. If you have
found any bug, please, report it
`there <https://storyboard.openstack.org/#!/project/912>`_.

**Important** information **to mention**:

  * **System** on which the problem occurred (e.g. CentOS, Ubuntu, ...)
  * The source of ``python-tempestconf`` you have used. The **package version
    number** in case of RPM or the **branch used** in case of installation from
    git.
  * The **exact command** with all arguments you have used.
  * It's always better to include the **console output** as well.


Requesting Features
-------------------

Create a story with a task for our
`project <https://storyboard.openstack.org/#!/project/912>`_ containing all the
relevant information, mainly:

  * **description** of the feature
  * **inputs** (new CLI option, ...) and **outputs** (desired configuration in
    tempest.conf) of the feature
  * the **reason why** it should be implemented


Fixing bugs
-----------

1. If you have found a bug and you know how to fix it, please, check our
   `storyboard project <https://storyboard.openstack.org/#!/project/912>`_ for
   any stories which may relate to the issue. If you haven't find any related
   story, please, create one. Check `Reporting Bugs`_.

2. Follow `Contributing Code`_ and submit a code review in
   https://review.opendev.org/.


Contributing Code
-----------------
Like any other project part of OpenStack, the development of
``python-tempestconf`` follows the OpenStack guidelines for contribution.

Learn `how to contribute into OpenStack <https://wiki.openstack.org/wiki/How_To_Contribute>`_.

If you have made any changes in the source code, **run tests locally before
posting a review**. You can do so by running tox.

If you've made any changes in the documentation (under ``doc/``) run::

    $ tox -edocs

If you've made any changes in the source code run unit tests as follows::

    $ tox -epy27

and **pep8** check like following::

    $ tox -epep8

If you've written also a releasenote, make sure the syntax is correct by
running::

    $ tox -ereleasenotes

If you've made any changes which are related to a task in a story in our
`storyboard project <https://storyboard.openstack.org/#!/project/912>`_, please,
**include a story and task number in the commit message**.

