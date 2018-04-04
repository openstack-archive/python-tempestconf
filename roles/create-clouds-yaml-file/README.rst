Creates clouds.yaml file

Source credentials and create a clouds.yaml file. If the clouds.yaml
file in the defined location exists, it will be overwritten.
Note: If there is a file int the location, where clouds_file_path points, called
openstack, it will be removed and directory called openstack will be created.

**Role Variables**

.. zuul:rolevar:: clouds_file_path
   :type: string
   :default: /etc/openstack/clouds.yaml

    A path to the clouds.yaml file.

.. zuul:rolevar:: source_credentials_commands
   :type: string
   :default: None

    A file or command to be sourced for obtaining credentials.

.. zuul:rolevar:: cloudname
   :type: string
   :default: None

    A cloudname under which will be sourced credentials saved
    in clouds.yaml file

