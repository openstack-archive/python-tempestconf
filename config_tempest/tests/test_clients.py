# -*- coding: utf-8 -*-

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

from fixtures import MonkeyPatch

from config_tempest.clients import ClientManager
from config_tempest.clients import ProjectsClient
from config_tempest.tests.base import BaseConfigTempestTest
from tempest.lib import exceptions


class TestProjectsClient(BaseConfigTempestTest):
    LIST_PROJECTS = [{'name': 'my_name'}]

    def setUp(self):
        super(TestProjectsClient, self).setUp()
        self.conf = self._get_conf("v2.0", "v3")
        self.creds = self._get_creds(self.conf)
        # self.projects_manager = ProjectsClient(self.conf, self.creds)
        self.client_manager = ClientManager(self.conf, self.creds)

    def _get_projects_client(self, identity_version):
        return ProjectsClient(
            self.client_manager.auth_provider,
            self.conf.get_defaulted('identity', 'catalog_type'),
            self.client_manager.identity_region,
            'publicURL',
            identity_version,
            **self.client_manager._get_default_params(self.conf))

    def test_init(self):
        resp = self._get_projects_client('v2')
        self.assertEqual(type(resp.client).__name__, 'TenantsClient')
        # use v3 identity version and check if ProjectClient is instantiated
        resp = self._get_projects_client('v3')
        self.assertEqual(type(resp.client).__name__, 'ProjectsClient')

    @mock.patch('tempest.lib.services.identity.v2.tenants_client.'
                'TenantsClient.list_tenants')
    def test_get_project_by_name_v2(self, mock_list_tenant):
        client = self._get_projects_client('v2')
        mock_list_tenant.return_value = {'tenants': self.LIST_PROJECTS}
        resp = client.get_project_by_name('my_name')
        self.assertEqual(resp['name'], 'my_name')

    @mock.patch('tempest.lib.services.identity.v3.projects_client.'
                'ProjectsClient.list_projects')
    def test_get_project_by_name_v3(self, mock_list_project):
        client = self._get_projects_client('v3')
        mock_list_project.return_value = {'projects': self.LIST_PROJECTS}
        resp = client.get_project_by_name('my_name')
        self.assertEqual(resp['name'], 'my_name')

    @mock.patch('tempest.lib.services.identity.v3.projects_client.'
                'ProjectsClient.list_projects')
    def test_get_project_by_name_not_found(self, mock_list_project):
        client = self._get_projects_client('v3')
        mock_list_project.return_value = {'projects': self.LIST_PROJECTS}
        try:
            client.get_project_by_name('doesnt_exist')
        except exceptions.NotFound:
            # expected behaviour
            pass

    @mock.patch('tempest.lib.services.identity.v2.tenants_client.'
                'TenantsClient.create_tenant')
    def test_create_project_v2(self, mock_create_tenant):
        client = self._get_projects_client('v2')
        client.create_project('name', 'description')
        mock_create_tenant.assert_called_with(
            name='name', description='description')

    @mock.patch('tempest.lib.services.identity.v3.projects_client.'
                'ProjectsClient.create_project')
    def test_create_project_v3(self, mock_create_project):
        client = self._get_projects_client('v3')
        client.create_project('name', 'description')
        mock_create_project.assert_called_with(
            name='name', description='description')


class TestClientManager(BaseConfigTempestTest):

    def setUp(self):
        super(TestClientManager, self).setUp()
        self.conf = self._get_conf("v2.0", "v3")
        self.creds = self._get_creds(self.conf)
        # self.client = self._get_clients(self.conf)  # ?
        self.client_manager = ClientManager(self.conf, self.creds)

    def test_init_manager_as_admin(self):
        self.creds = self._get_creds(self.conf, True)
        mock_function = mock.Mock(return_value={"id": "my_fake_id"})
        func2mock = ('config_tempest.clients.ProjectsClient.'
                     'get_project_by_name')
        self.useFixture(MonkeyPatch(func2mock, mock_function))
        ClientManager(self.conf, self.creds)
        # check if admin project id was set
        admin_project_id = self.conf.get("auth", "admin_project_id")
        self.assertEqual(admin_project_id, "my_fake_id")

    def test_get_service_client(self):
        resp = self.client_manager.get_service_client('image')
        self.assertEqual(resp, self.client_manager.images)
        resp = self.client_manager.get_service_client('network')
        self.assertEqual(resp, self.client_manager)
        resp = self.client_manager.get_service_client('doesnt_exist')
        self.assertEqual(resp, None)

    def test_set_users_client(self):
        self.client_manager.users = None
        self.client_manager.set_users_client(
            self.client_manager.auth_provider,
            self.creds.identity_version,
            self.conf.get_defaulted('identity', 'catalog_type'),
            'publicURL',
            self.client_manager._get_default_params(self.conf))
        self.assertEqual(
            type(self.client_manager.users).__name__,
            'UsersClient')

    def test_set_roles_client(self):
        self.client_manager.roles = None
        self.client_manager.set_roles_client(
            self.client_manager.auth_provider,
            self.creds.identity_version,
            self.conf.get_defaulted('identity', 'catalog_type'),
            'publicURL',
            self.client_manager._get_default_params(self.conf))
        self.assertEqual(
            type(self.client_manager.roles).__name__,
            'RolesClient')
