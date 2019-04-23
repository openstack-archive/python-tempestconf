============
Installation
============

Git
---

1. Clone and change to the directory::

    $ git clone https://opendev.org/openstack/python-tempestconf
    $ cd python-tempestconf

2. Create a virtual environment using :command:`virtualenv`::

    $ virtualenv .venv
    $ source .venv/bin/activate

3. Install requirements in the newly created virtual environment::

    (.venv) $ pip install .

4. *(optional)* Instead of manual installation described in steps 2 and 3
   above, tox can be used for installing the requirements as well.
   To create python 2.7 environment run following::

    $ tox -epy27
    $ source .tox/py27/bin/activate

   and python 3.5 environment can be created as follows::

    $ tox -epy35
    $ source .tox/py35/bin/activate


RPM Installation (RDO)
----------------------

* ``python-tempestconf`` package can be installed as follows::

    $ sudo yum install python-tempestconf

* ``python-tempestconf`` is installed together with ``openstack-tempest``, as
  a new dependency (starting **from** the **Ocata** release)::

    $ sudo yum install openstack-tempest


Pip installation
----------------

Install ``python-tempestconf`` via pip as follows::

   $ pip install python-tempestconf
