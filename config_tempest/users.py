# Copyright 2016, 2018 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from config_tempest.constants import LOG
from tempest.lib import exceptions


class Users(object):
    def __init__(self, projects_client, roles_client, users_client, conf):
        """Init.

        :type projects_client: ProjectsClient object
        :type roles_client: RolesClient object from tempest lib
        :type users_client: UsersClient object from tempest lib
        :type conf: TempestConf object
        """
        self.projects_client = projects_client
        self.roles_client = roles_client
        self.users_client = users_client
        self._conf = conf

    def create_tempest_users(self, orchestration=False):
        """Create users necessary for Tempest if they don't exist already.

        :type orchestration: boolean
        """
        sec = 'identity'
        self.create_user_with_project(self._conf.get(sec, 'username'),
                                      self._conf.get(sec, 'password'),
                                      self._conf.get(sec, 'project_name'))

        self.create_user_with_project(self._conf.get(sec, 'alt_username'),
                                      self._conf.get(sec, 'alt_password'),
                                      self._conf.get(sec, 'alt_project_name'))

        username = self._conf.get_defaulted('auth', 'admin_username')

        self.give_role_to_user(username, role_name='admin')

        # Prior to juno, and with earlier juno defaults, users needed to have
        # the heat_stack_owner role to use heat stack apis. We assign that role
        # to the user if the role is present.
        if orchestration:
            self.give_role_to_user(self._conf.get('identity', 'username'),
                                   role_name='heat_stack_owner',
                                   role_required=False)

    def give_role_to_user(self, username, role_name,
                          role_required=True):
        """Give the user a role in the project.

        :type username: string
        :type role_name: string
        :type role_required: boolean
        """
        project_name = self._conf.get('identity', 'project_name')
        proj_id = self.projects_client.get_project_by_name(project_name)['id']
        users = self.users_client.list_users()
        user_ids = [u['id'] for u in users['users'] if u['name'] == username]
        user_id = user_ids[0]
        roles = self.roles_client.list_roles()
        role_ids = [r['id'] for r in roles['roles'] if r['name'] == role_name]
        if not role_ids:
            if role_required:
                raise Exception("required role %s not found" % role_name)
            LOG.debug("%s role not required", role_name)
            return
        role_id = role_ids[0]
        try:
            self.roles_client.create_user_role_on_project(proj_id, user_id,
                                                          role_id)
            LOG.debug("User '%s' was given the '%s' role in project '%s'",
                      username, role_name, project_name)
        except exceptions.Conflict:
            LOG.debug("(no change) User '%s' already has the '%s' role in"
                      " project '%s'", username, role_name, project_name)

    def create_user_with_project(self, username, password, project_name):
        """Create a user and a project if it doesn't exist.

        :type username: string
        :type password: string
        :type project_name: string
        """
        LOG.info("Creating user '%s' with project '%s' and password '%s'",
                 username, project_name, password)
        project_description = "Project for Tempest %s user" % username
        email = "%s@test.com" % username
        # create a project
        try:
            self.projects_client.create_project(
                name=project_name, description=project_description)
        except exceptions.Conflict:
            LOG.info("(no change) Project '%s' already exists", project_name)

        proj_id = self.projects_client.get_project_by_name(project_name)['id']

        params = {'name': username, 'password': password,
                  'tenantId': proj_id, 'email': email}
        # create a user
        try:
            self.users_client.create_user(**params)
        except exceptions.Conflict:
            LOG.info("User '%s' already exists.", username)
