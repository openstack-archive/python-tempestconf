Workaround clouds.yaml file
===========================

Workaround for AUTH URL in clouds.yaml file.
auth_url needs to be edited in devstack environment so that
it contains "/v3" as a suffix.

**Role Variables**

.. zuul:rolevar:: clouds_file_path
   :type: string
   :default: /etc/openstack/clouds.yaml

   A path to the clouds.yaml file.

