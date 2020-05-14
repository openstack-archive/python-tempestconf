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

from unittest import mock

from fixtures import MonkeyPatch

from config_tempest.clients import ClientManager
from config_tempest import main as tool
from config_tempest import tempest_conf
from config_tempest.tests.base import BaseConfigTempestTest


class TestOsClientConfigSupport(BaseConfigTempestTest):

    def setUp(self):
        super(TestOsClientConfigSupport, self).setUp()
        self.conf = self._get_conf("v2.0", "v3")

    def _check_credentials(self, manager, username, password, project_name):
        exp_user = manager.auth_provider.credentials._initial['username']
        exp_pass = manager.auth_provider.credentials._initial['password']
        creds = manager.auth_provider.credentials
        exp_project = creds._initial['project_name']
        self.assertEqual(exp_user, username)
        self.assertEqual(exp_pass, password)
        self.assertEqual(exp_project, project_name)

    def _override_setup(self):
        mock_function = mock.Mock(return_value={"id": "my_fake_id"})
        func2mock = ('config_tempest.clients.ProjectsClient.'
                     'get_project_by_name')
        self.useFixture(MonkeyPatch(func2mock, mock_function))

    def _obtain_client_config_data(self, non_admin=True, region_name=None):
        cloud_args = {
            'username': 'cloud_user',
            'password': 'cloud_pass',
            'project_name': 'cloud_project',
            'auth_url': 'http://auth.url.com/'
        }
        if region_name:
            cloud_args.update(region_name=region_name)
        # create an empty conf
        conf = tempest_conf.TempestConf()
        conf.set('identity', 'uri', cloud_args['auth_url'], priority=True)
        # call the function and check if data were obtained properly
        tool.set_cloud_config_values(non_admin, cloud_args, conf)
        if non_admin:
            self.assertEqual(cloud_args['username'],
                             conf.get('identity', 'username'))
            self.assertEqual(cloud_args['password'],
                             conf.get('identity', 'password'))
            self.assertEqual(cloud_args['project_name'],
                             conf.get('identity', 'project_name'))
        else:
            self.assertEqual(cloud_args['username'],
                             conf.get('auth', 'admin_username'))
            self.assertEqual(cloud_args['password'],
                             conf.get('auth', 'admin_password'))
            self.assertEqual(cloud_args['project_name'],
                             conf.get('auth', 'admin_project_name'))
        if region_name:
            self.assertEqual(cloud_args['region_name'],
                             conf.get('identity', 'region'))

    def test_init_manager_client_config(self):
        self._obtain_client_config_data()

    def test_init_manager_client_config_as_admin(self):
        self._obtain_client_config_data(non_admin=False)

    def test_init_manager_client_config_region_name(self):
        self._obtain_client_config_data(region_name='regionOne')

    def test_init_manager_client_config_get_default(self):
        manager = ClientManager(self.conf, self._get_creds(self.conf))
        # cloud_args is empty => check if default credentials were used
        self._check_credentials(manager,
                                self.conf.get('identity', 'username'),
                                self.conf.get('identity', 'password'),
                                self.conf.get('identity', 'project_name'))

    def test_init_manager_client_config_override(self):
        self._override_setup()
        manager = ClientManager(self.conf, self._get_creds(self.conf))
        # check if cloud_args credentials were overrided by the ones set in CLI
        self._check_credentials(manager,
                                self.conf.get('identity', 'username'),
                                self.conf.get('identity', 'password'),
                                self.conf.get('identity', 'project_name'))

    def test_init_manager_client_config_admin_override(self):
        self._override_setup()
        creds = self._get_creds(self.conf, admin=True)
        manager = ClientManager(self.conf, creds)
        # check if cloud_args credentials were overrided by admin ones
        self._check_credentials(manager,
                                self.conf.get('auth', 'admin_username'),
                                self.conf.get('auth', 'admin_password'),
                                self.conf.get('auth', 'admin_project_name'))
