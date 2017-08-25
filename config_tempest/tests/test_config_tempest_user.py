# -*- coding: utf-8 -*-

# Copyright 2017 Red Hat, Inc.
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

from config_tempest import config_tempest as tool
from config_tempest.tests.base import BaseConfigTempestTest
import mock
from tempest.lib import exceptions


class TestCreateTempestUser(BaseConfigTempestTest):

    def setUp(self):
        super(TestCreateTempestUser, self).setUp()
        self.conf = self._get_conf("v2.0", "v3")
        self.tenants_client = self._get_clients(self.conf).tenants
        self.users_client = self._get_clients(self.conf).users
        self.roles_client = self._get_clients(self.conf).roles

    @mock.patch('config_tempest.config_tempest.'
                'create_user_with_tenant')
    @mock.patch('config_tempest.config_tempest.give_role_to_user')
    def _test_create_tempest_user(self,
                                  mock_give_role_to_user,
                                  mock_create_user_with_tenant,
                                  services):
        alt_username = "my_user"
        alt_password = "my_pass"
        alt_tenant_name = "my_tenant"
        self.conf.set("identity", "alt_username", alt_username)
        self.conf.set("identity", "alt_password", alt_password)
        self.conf.set("identity", "alt_tenant_name", alt_tenant_name)
        tool.create_tempest_users(self.tenants_client,
                                  self.roles_client,
                                  self.users_client,
                                  self.conf,
                                  services=services)
        if 'orchestration' in services:
            self.assertEqual(mock_give_role_to_user.mock_calls, [
                mock.call(self.tenants_client,
                          self.roles_client,
                          self.users_client,
                          self.conf.get('identity',
                                        'admin_username'),
                          self.conf.get('identity',
                                        'tenant_name'),
                          role_name='admin'),
                mock.call(self.tenants_client,
                          self.roles_client,
                          self.users_client,
                          self.conf.get('identity',
                                        'username'),
                          self.conf.get('identity',
                                        'tenant_name'),
                          role_name='heat_stack_owner',
                          role_required=False),
            ])
        else:
            mock_give_role_to_user.assert_called_with(
                self.tenants_client, self.roles_client,
                self.users_client,
                self.conf.get('identity', 'admin_username'),
                self.conf.get('identity', 'tenant_name'),
                role_name='admin')
        self.assertEqual(mock_create_user_with_tenant.mock_calls, [
            mock.call(self.tenants_client,
                      self.users_client,
                      self.conf.get('identity', 'username'),
                      self.conf.get('identity', 'password'),
                      self.conf.get('identity', 'tenant_name')),
            mock.call(self.tenants_client,
                      self.users_client,
                      self.conf.get('identity', 'alt_username'),
                      self.conf.get('identity', 'alt_password'),
                      self.conf.get('identity', 'alt_tenant_name')),
        ])

    def test_create_tempest_user(self):
        services = ['compute', 'network']
        self._test_create_tempest_user(services=services)

    def test_create_tempest_user_with_orchestration(self):
        services = ['compute', 'network', 'orchestration']
        self._test_create_tempest_user(services=services)


class TestCreateUserWithTenant(BaseConfigTempestTest):

    def setUp(self):
        super(TestCreateUserWithTenant, self).setUp()
        self.conf = self._get_conf("v2.0", "v3")
        self.tenants_client = self._get_clients(self.conf).tenants
        self.users_client = self._get_clients(self.conf).users
        self.username = "test_user"
        self.password = "cryptic"
        self.tenant_name = "project"
        self.tenant_description = "Tenant for Tempest %s user" % self.username
        self.email = "%s@test.com" % self.username

    @mock.patch('config_tempest.config_tempest.ProjectsClient'
                '.get_project_by_name')
    @mock.patch('config_tempest.config_tempest.ProjectsClient.create_project')
    @mock.patch('tempest.lib.services.identity.v2.users_client.'
                'UsersClient.create_user')
    def test_create_user_with_tenant(self,
                                     mock_create_user,
                                     mock_create_project,
                                     mock_get_project_by_name):
        mock_get_project_by_name.return_value = {'id': "fake-id"}
        tool.create_user_with_tenant(
            tenants_client=self.tenants_client,
            users_client=self.users_client,
            username=self.username,
            password=self.password,
            tenant_name=self.tenant_name)
        mock_create_project.assert_called_with(
            name=self.tenant_name, description=self.tenant_description)
        mock_create_user.assert_called_with(name=self.username,
                                            password=self.password,
                                            tenantId="fake-id",
                                            email=self.email)

    @mock.patch('config_tempest.config_tempest.ProjectsClient'
                '.get_project_by_name')
    @mock.patch('config_tempest.config_tempest.ProjectsClient.create_project')
    @mock.patch('tempest.lib.services.identity.v2'
                '.users_client.UsersClient.create_user')
    def test_create_user_with_tenant_tenant_exists(
            self,
            mock_create_user,
            mock_create_project,
            mock_get_project_by_name):
        mock_get_project_by_name.return_value = {'id': "fake-id"}
        exc = exceptions.Conflict
        mock_create_project.side_effect = exc
        tool.create_user_with_tenant(
            tenants_client=self.tenants_client,
            users_client=self.users_client,
            username=self.username,
            password=self.password,
            tenant_name=self.tenant_name)
        mock_create_project.assert_called_with(
            name=self.tenant_name, description=self.tenant_description)
        mock_create_user.assert_called_with(
            name=self.username,
            password=self.password,
            tenantId="fake-id",
            email=self.email)

    @mock.patch('tempest.lib.services.identity.v2.'
                'users_client.UsersClient.update_user_password')
    @mock.patch('tempest.common.identity.get_user_by_username')
    @mock.patch('config_tempest.config_tempest.ProjectsClient.'
                'get_project_by_name')
    @mock.patch('tempest.lib.services.identity.v2.'
                'tenants_client.TenantsClient.create_tenant')
    @mock.patch('tempest.lib.services.identity.'
                'v2.users_client.UsersClient.create_user')
    def test_create_user_with_tenant_user_exists(
            self, mock_create_user, mock_create_tenant,
            mock_get_project_by_name,
            mock_get_user_by_username,
            mock_update_user_password):
        mock_get_project_by_name.return_value = {'id': "fake-id"}
        exc = exceptions.Conflict
        mock_create_user.side_effect = exc
        fake_user = {'id': "fake_user_id"}
        mock_get_user_by_username.return_value = fake_user
        tool.create_user_with_tenant(
            tenants_client=self.tenants_client,
            users_client=self.users_client,
            username=self.username, password=self.password,
            tenant_name=self.tenant_name)
        mock_create_tenant.assert_called_with(
            name=self.tenant_name, description=self.tenant_description)
        mock_create_user.assert_called_with(name=self.username,
                                            password=self.password,
                                            tenantId="fake-id",
                                            email=self.email)

    @mock.patch('tempest.lib.services.identity.v2.'
                'users_client.UsersClient.update_user_password')
    @mock.patch('tempest.common.identity.get_user_by_username')
    @mock.patch('config_tempest.config_tempest.ProjectsClient.'
                'get_project_by_name')
    @mock.patch('config_tempest.config_tempest.ProjectsClient.create_project')
    @mock.patch('tempest.lib.services.identity.v2.'
                'users_client.UsersClient.create_user')
    def test_create_user_with_tenant_exists_user_exists(
            self, mock_create_user, mock_create_project,
            mock_get_project_by_name,
            mock_get_user_by_username,
            mock_update_user_password):
        mock_get_project_by_name.return_value = {'id': "fake-id"}
        exc = exceptions.Conflict
        mock_create_project.side_effects = exc
        mock_create_user.side_effect = exc
        fake_user = {'id': "fake_user_id"}
        mock_get_user_by_username.return_value = fake_user
        tool.create_user_with_tenant(tenants_client=self.tenants_client,
                                     users_client=self.users_client,
                                     username=self.username,
                                     password=self.password,
                                     tenant_name=self.tenant_name)
        mock_create_project.assert_called_with(
            name=self.tenant_name, description=self.tenant_description)
        mock_create_user.assert_called_with(name=self.username,
                                            password=self.password,
                                            tenantId="fake-id",
                                            email=self.email)


class TestGiveRoleToUser(BaseConfigTempestTest):

    def setUp(self):
        super(TestGiveRoleToUser, self).setUp()
        self.conf = self._get_conf("v2.0", "v3")
        self.tenants_client = self._get_clients(self.conf).tenants
        self.users_client = self._get_clients(self.conf).users
        self.roles_client = self._get_clients(self.conf).roles
        self.username = "test_user"
        self.tenant_name = "project"
        self.role_name = "fake_role"
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

    @mock.patch('config_tempest.config_tempest.ProjectsClient.'
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
            {'id': "fake_tenant_id"}
        mock_list_users.return_value = self.users
        mock_list_roles.return_value = self.roles
        tool.give_role_to_user(
            tenants_client=self.tenants_client,
            roles_client=self.roles_client,
            users_client=self.users_client,
            username=self.username,
            tenant_name=self.tenant_name,
            role_name=self.role_name)
        mock_create_user_role_on_project.assert_called_with(
            "fake_tenant_id", "fake_user_id", "fake_role_id")

    @mock.patch('config_tempest.config_tempest.ProjectsClient.'
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
            {'id': "fake_tenant_id"}
        mock_list_users.return_value = self.users
        mock_list_roles.return_value = self.roles
        exc = Exception
        self.assertRaises(exc,
                          tool.give_role_to_user,
                          tenants_client=self.tenants_client,
                          roles_client=self.roles_client,
                          users_client=self.users_client,
                          username=self.username,
                          tenant_name=self.tenant_name,
                          role_name=role_name)

    @mock.patch('config_tempest.config_tempest.ProjectsClient.'
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
            {'id': "fake_tenant_id"}
        mock_list_users.return_value = self.users
        mock_list_roles.return_value = self.roles
        tool.give_role_to_user(
            tenants_client=self.tenants_client,
            roles_client=self.roles_client,
            users_client=self.users_client,
            username=self.username,
            tenant_name=self.tenant_name,
            role_name=self.role_name,
            role_required=False)

    @mock.patch('config_tempest.config_tempest.ProjectsClient'
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
        mock_get_project_by_name.return_value = {'id': "fake_tenant_id"}
        mock_list_users.return_value = self.users
        mock_list_roles.return_value = self.roles
        tool.give_role_to_user(
            tenants_client=self.tenants_client,
            roles_client=self.roles_client,
            users_client=self.users_client,
            username=self.username,
            tenant_name=self.tenant_name,
            role_name=self.role_name)
