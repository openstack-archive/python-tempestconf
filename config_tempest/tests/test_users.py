# Copyright 2018 Red Hat, Inc.
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

from unittest import mock

from config_tempest.tests.base import BaseConfigTempestTest
from config_tempest.users import Users
from tempest.lib import exceptions


class TestUsers(BaseConfigTempestTest):

    def setUp(self):
        # TODO(arxcruz): All these tests are running on identity v2 only, we
        # need to create tests for v3 too!
        # Story 2003388
        super(TestUsers, self).setUp()
        self.conf = self._get_conf("v2.0", "v3")
        self.conf.set("auth", "tempest_roles", "fake_role")
        projects_client = self._get_clients(self.conf).projects
        users_client = self._get_clients(self.conf).users
        roles_client = self._get_clients(self.conf).roles
        self.Service = Users(projects_client, roles_client,
                             users_client, self.conf)
        self.username = "test_user"
        self.password = "cryptic"
        self.project_name = "project"
        description = "Project for Tempest %s user" % self.username
        self.project_description = description
        self.role_name = "fake_role"
        self.email = "%s@test.com" % self.username
        self.users = {'users':
                      [{'name': "test_user",
                        'id': "fake_user_id"},
                       {'name': "test_user2",
                        'id': "fake_user_id2"}]}
        self.roles = {'roles':
                      [{'name': "fake_role",
                        'id': "fake_role_id"},
                       {'name': "fake_role2",
                        'id': "fake_role_id2"}]}

    @mock.patch('config_tempest.users.Users.'
                'create_user_with_project')
    @mock.patch('config_tempest.users.Users.give_role_to_user')
    def _test_create_tempest_user(self,
                                  mock_give_role_to_user,
                                  mock_create_user_with_project):
        alt_username = "my_user"
        alt_password = "my_pass"
        alt_project_name = "my_project"
        self.conf.set("identity", "alt_username", alt_username)
        self.conf.set("identity", "alt_password", alt_password)
        self.conf.set("identity", "alt_project_name", alt_project_name)
        self.Service.create_tempest_users()
        mock_give_role_to_user.assert_called_with(
            self.conf.get('auth', 'admin_username'),
            role_name='admin')
        self.assertEqual(mock_create_user_with_project.mock_calls, [
            mock.call(self.conf.get('identity', 'username'),
                      self.conf.get('identity', 'password'),
                      self.conf.get('identity', 'project_name')),
            mock.call(self.conf.get('identity', 'alt_username'),
                      self.conf.get('identity', 'alt_password'),
                      self.conf.get('identity', 'alt_project_name')),
        ])

    def test_create_tempest_user(self):
        self._test_create_tempest_user()

    @mock.patch('config_tempest.clients.ProjectsClient'
                '.get_project_by_name')
    @mock.patch('config_tempest.clients.ProjectsClient.create_project')
    @mock.patch('tempest.lib.services.identity.v2.users_client.'
                'UsersClient.create_user')
    def test_create_user_with_project(self,
                                      mock_create_user,
                                      mock_create_project,
                                      mock_get_project_by_name):
        mock_get_project_by_name.return_value = {'id': "fake-id"}
        self.Service.create_user_with_project(
            username=self.username,
            password=self.password,
            project_name=self.project_name)
        mock_create_project.assert_called_with(
            name=self.project_name, description=self.project_description)
        mock_create_user.assert_called_with(name=self.username,
                                            password=self.password,
                                            tenantId="fake-id",
                                            email=self.email)

    @mock.patch('config_tempest.clients.ProjectsClient'
                '.get_project_by_name')
    @mock.patch('config_tempest.clients.ProjectsClient.create_project')
    @mock.patch('tempest.lib.services.identity.v2'
                '.users_client.UsersClient.create_user')
    def test_create_user_with_project_project_exists(
            self,
            mock_create_user,
            mock_create_project,
            mock_get_project_by_name):
        mock_get_project_by_name.return_value = {'id': "fake-id"}
        exc = exceptions.Conflict
        mock_create_project.side_effect = exc
        self.Service.create_user_with_project(
            username=self.username,
            password=self.password,
            project_name=self.project_name)
        mock_create_project.assert_called_with(
            name=self.project_name, description=self.project_description)
        mock_create_user.assert_called_with(
            name=self.username,
            password=self.password,
            tenantId="fake-id",
            email=self.email)

    @mock.patch('tempest.common.identity.get_user_by_username')
    @mock.patch('config_tempest.clients.ProjectsClient.'
                'get_project_by_name')
    @mock.patch('tempest.lib.services.identity.v2.'
                'tenants_client.TenantsClient.create_tenant')
    @mock.patch('tempest.lib.services.identity.'
                'v2.users_client.UsersClient.create_user')
    def test_create_user_with_project_user_exists(
            self, mock_create_user, mock_create_project,
            mock_get_project_by_name,
            mock_get_user_by_username):
        mock_get_project_by_name.return_value = {'id': "fake-id"}
        exc = exceptions.Conflict
        mock_create_user.side_effect = exc
        fake_user = {'id': "fake_user_id"}
        mock_get_user_by_username.return_value = fake_user
        self.Service.create_user_with_project(
            username=self.username, password=self.password,
            project_name=self.project_name)
        mock_create_project.assert_called_with(
            name=self.project_name, description=self.project_description)
        mock_create_user.assert_called_with(name=self.username,
                                            password=self.password,
                                            tenantId="fake-id",
                                            email=self.email)

    @mock.patch('tempest.common.identity.get_user_by_username')
    @mock.patch('config_tempest.clients.ProjectsClient.'
                'get_project_by_name')
    @mock.patch('config_tempest.clients.ProjectsClient.create_project')
    @mock.patch('tempest.lib.services.identity.v2.'
                'users_client.UsersClient.create_user')
    def test_create_user_with_project_exists_user_exists(
            self, mock_create_user, mock_create_project,
            mock_get_project_by_name,
            mock_get_user_by_username):
        mock_get_project_by_name.return_value = {'id': "fake-id"}
        exc = exceptions.Conflict
        mock_create_project.side_effects = exc
        mock_create_user.side_effect = exc
        fake_user = {'id': "fake_user_id"}
        mock_get_user_by_username.return_value = fake_user
        self.Service.create_user_with_project(username=self.username,
                                              password=self.password,
                                              project_name=self.project_name)
        mock_create_project.assert_called_with(
            name=self.project_name, description=self.project_description)
        mock_create_user.assert_called_with(name=self.username,
                                            password=self.password,
                                            tenantId="fake-id",
                                            email=self.email)

    @mock.patch('config_tempest.clients.ProjectsClient.'
                'get_project_by_name')
    @mock.patch('tempest.lib.services.identity.v2.'
                'users_client.UsersClient.list_users')
    @mock.patch('tempest.lib.services.identity.v2.'
                'users_client.UsersClient.create_user')
    @mock.patch('tempest.lib.services.identity.v2.'
                'roles_client.RolesClient.list_roles')
    @mock.patch('tempest.lib.services.identity.v2.''roles_client.'
                'RolesClient.create_user_role_on_project')
    def test_give_role_to_user(self,
                               mock_create_user_role_on_project,
                               mock_list_roles,
                               mock_create_user,
                               mock_list_users,
                               mock_get_project_by_name):

        mock_get_project_by_name.return_value = \
            {'id': "fake_project_id"}
        mock_list_users.return_value = self.users
        mock_list_roles.return_value = self.roles
        self.Service.give_role_to_user(
            username=self.username,
            role_name=self.role_name)
        mock_create_user_role_on_project.assert_called_with(
            "fake_project_id", "fake_user_id", "fake_role_id")

    @mock.patch('config_tempest.clients.ProjectsClient.'
                'get_project_by_name')
    @mock.patch('tempest.lib.services.identity.'
                'v2.users_client.UsersClient.list_users')
    @mock.patch('tempest.lib.services.identity.v2.'
                'users_client.UsersClient.create_user')
    @mock.patch('tempest.lib.services.identity.v2.'
                'roles_client.RolesClient.list_roles')
    @mock.patch('tempest.lib.services.identity.v2.'
                'roles_client.RolesClient.create_user_role_on_project')
    def test_give_role_to_user_role_not_found(
            self,
            mock_create_user_role_on_project,
            mock_list_roles,
            mock_create_user,
            mock_list_users,
            mock_get_project_by_name):
        role_name = "fake_role_that_does_not_exist"
        mock_get_project_by_name.return_value = \
            {'id': "fake_project_id"}
        mock_list_users.return_value = self.users
        mock_list_roles.return_value = self.roles
        exc = Exception
        self.assertRaises(exc,
                          self.Service.give_role_to_user,
                          username=self.username,
                          role_name=role_name)

    @mock.patch('config_tempest.clients.ProjectsClient.'
                'get_project_by_name')
    @mock.patch('tempest.lib.services.identity.v2.'
                'users_client.UsersClient.list_users')
    @mock.patch('tempest.lib.services.identity.v2.'
                'users_client.UsersClient.create_user')
    @mock.patch('tempest.lib.services.identity.v2.'
                'roles_client.RolesClient.list_roles')
    @mock.patch('tempest.lib.services.identity.v2.roles_client'
                '.RolesClient.create_user_role_on_project')
    def test_give_role_to_user_role_not_found_not_req(
            self,
            mock_create_user_role_on_project,
            mock_list_roles,
            mock_create_user,
            mock_list_users,
            mock_get_project_by_name):

        mock_get_project_by_name.return_value = \
            {'id': "fake_project_id"}
        mock_list_users.return_value = self.users
        mock_list_roles.return_value = self.roles
        self.Service.give_role_to_user(
            username=self.username,
            role_name=self.role_name,
            role_required=False)

    @mock.patch('config_tempest.clients.ProjectsClient'
                '.get_project_by_name')
    @mock.patch('tempest.lib.services.identity.v2.'
                'users_client.UsersClient.list_users')
    @mock.patch('tempest.lib.services.identity.v2.'
                'users_client.UsersClient.create_user')
    @mock.patch('tempest.lib.services.identity.v2.'
                'roles_client.RolesClient.list_roles')
    @mock.patch('tempest.lib.services.identity.v2.roles_client.'
                'RolesClient.create_user_role_on_project')
    def test_give_role_to_user_role_already_given(
            self,
            mock_create_user_role_on_project,
            mock_list_roles,
            mock_create_user,
            mock_list_users,
            mock_get_project_by_name):
        exc = exceptions.Conflict
        mock_create_user_role_on_project.side_effect = exc
        mock_get_project_by_name.return_value = {'id': "fake_project_id"}
        mock_list_users.return_value = self.users
        mock_list_roles.return_value = self.roles
        self.Service.give_role_to_user(
            username=self.username,
            role_name=self.role_name)

    def _check_user_roles(self, user_roles, system_roles):
        self.Service._conf.set('auth', 'tempest_roles', user_roles)
        return self.Service.check_user_roles(system_roles)

    @mock.patch('logging.Logger.debug')
    def _check_user_role_does_not_exist(self, system_roles, LOG_mock,
                                        default_role='member'):
        roles = self._check_user_roles('doesNotExist', system_roles)
        # check if it fell down to member
        conf = self.Service._conf
        self.assertEqual(conf.get('auth', 'tempest_roles'), default_role)
        self.assertEqual(roles, [])
        self.assertEqual(len(LOG_mock.mock_calls), 3)

    def test_check_user_role_exists(self):
        system_roles = {'roles': [{'name': 'role1'}, {'name': 'role2'}]}
        roles = self._check_user_roles('role1', system_roles)
        self.assertEqual(roles[0], 'role1')

    @mock.patch('logging.Logger.debug')
    def test_check_user_roles_one_exists(self, LOG_mock):
        system_roles = {'roles': [{'name': 'role1'}, {'name': 'role2'}]}
        roles = self._check_user_roles('role1, doesNotExist', system_roles)
        self.assertEqual(roles[0], 'role1')
        self.assertEqual(len(LOG_mock.mock_calls), 2)

    @mock.patch('logging.Logger.debug')
    def test_check_user_roles_two_exist(self, LOG_mock):
        system_roles = {'roles': [{'name': 'role1'}, {'name': 'role2'}]}
        roles = self._check_user_roles('role1,role2', system_roles)
        self.assertEqual(roles[0], 'role1')
        self.assertEqual(roles[1], 'role2')
        self.assertEqual(len(LOG_mock.mock_calls), 1)

    def test_check_user_role_does_not_exist_fall_to_member(self):
        system_roles = {'roles': [{'name': 'role1'}, {'name': 'member'}]}
        self._check_user_role_does_not_exist(system_roles)

    def test_check_user_role_does_not_exist_fall_to_Member(self):
        system_roles = {'roles': [{'name': 'role1'}, {'name': 'Member'}]}
        self._check_user_role_does_not_exist(system_roles,
                                             default_role='Member')

    @mock.patch('logging.Logger.debug')
    def test_check_user_role_does_not_exist_no_member(self, LOG_mock):
        system_roles = {'roles': [{'name': 'role1'}]}
        roles = self._check_user_roles('doesNotExist', system_roles)
        self.assertEqual(roles, [])
        self.assertEqual(len(LOG_mock.mock_calls), 4)
