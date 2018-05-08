Create keystonerc files
=======================

Create keystonerc files for tempest, print them to the output and copy them
to the wanted destination.

**Role Variables**

.. zuul:rolevar:: admin_user
   :type: dict

   A dictionary of admin user credentials.

   .. zuul:rolevar:: username
      :default: admin

   .. zuul:rolevar:: password
      :default: packstack

   .. zuul:rolevar:: project_name
      :default: admin

   .. zuul:rolevar:: user_domain_name
      :default: Default

   .. zuul:rolevar:: project_domain_name
      :default: Default

   .. zuul:rolevar:: identity_api_version
      :default: 3

   .. zuul:rolevar:: keystonerc_destination
      :default: {{ ansible_user_dir }}/keystonerc_admin

.. zuul:rolevar:: demo_user
   :type: dict

   A dictionary of demo user credentials.

   .. zuul:rolevar:: username
      :default: demo

   .. zuul:rolevar:: password
      :default: packstack

   .. zuul:rolevar:: project_name
      :default: demo

   .. zuul:rolevar:: user_domain_name
      :default: Default

   .. zuul:rolevar:: project_domain_name
      :default: Default

   .. zuul:rolevar:: identity_api_version
      :default: 3

   .. zuul:rolevar:: keystonerc_destination
      :default: {{ ansible_user_dir }}/keystonerc_demo

