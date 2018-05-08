Creates clouds.yaml file
========================

Source credentials and create a clouds.yaml file. If the clouds.yaml
file in the defined location exists, it will be overwritten.
Note: If there is a file called openstack in the location, where
clouds_file_path points, it will be removed and directory called openstack
will be created.

**Role Variables**

.. zuul:rolevar:: clouds_file_path
   :type: string
   :default: /etc/openstack/clouds.yaml

   A path to the clouds.yaml file.

.. zuul:rolevar:: source_credentials_commands
   :type: string
   :default: None
   :required: True

   Commands divided by a semicolon which define obtaining credentials.
   They need to be defined in the playbook the role is called from.
   For example for devstack it's used ({{ devstack_base_dir}} is the location
   where run-devstack role copies devstack source files):

   `source {{ devstack_base_dir }}/devstack/openrc {{ user }} {{ user }}`

   and for packstack ({{ ansible_user_dir }} is the location where
   packstack generates rc files):

   `source {{ ansible_user_dir }}/keystonerc_{{ user }}`

.. zuul:rolevar:: cloudname
   :type: string
   :default: None
   :required: True

   A cloudname under which sourced credentials will be saved
   in clouds.yaml file.

