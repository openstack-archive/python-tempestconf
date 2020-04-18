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

from config_tempest.tests.base import BaseConfigTempestTest


class TestCredentials(BaseConfigTempestTest):

    def setUp(self):
        super(TestCredentials, self).setUp()
        self.conf = self._get_conf("v2.0", "v3")
        self.creds = self._get_creds(self.conf)
        self.creds_v2 = self._get_creds(self.conf, v2=True)

    def test_get_credential(self):
        # set conf containing the newer values (admin creds in auth section)
        self.creds._conf = self._get_alt_conf("v2.0", "v3")
        resp = self.creds.get_credential("username")
        self.assertEqual(resp, "demo")
        # set admin credentials
        self.creds.admin = True
        resp = self.creds.get_credential("username")
        self.assertEqual(resp, "admin")

    def test_get_identity_version_v2(self):
        resp = self.creds_v2._get_identity_version()
        self.assertEqual(resp, 'v2')

    def test_get_identity_version_v3(self):
        conf = self._get_conf("v3", "v3")  # uri has to be v3
        creds = self._get_creds(conf)
        resp = creds._get_identity_version()
        self.assertEqual(resp, 'v3')

    def test_get_creds_kwargs(self):
        expected_resp = {
            'username': 'demo',
            'password': 'secret',
            'project_name': 'demo'
        }
        self.assertEqual(self.creds_v2._get_creds_kwargs(), expected_resp)
        self.creds_v2.identity_version = 'v3'
        expected_resp = {
            'username': 'demo',
            'password': 'secret',
            'project_name': 'demo',
            'domain_name': 'Default',
            'user_domain_name': 'Default'
        }
        self.assertEqual(self.creds._get_creds_kwargs(), expected_resp)

    def test_set_credentials_v2(self):
        mock_function = mock.Mock()
        function2mock = 'config_tempest.credentials.auth.get_credentials'
        self.useFixture(MonkeyPatch(function2mock, mock_function))
        self.creds_v2.username = "name"
        self.creds_v2.password = "pass"
        self.creds_v2.project_name = "Tname"
        self.creds_v2.set_credentials()
        mock_function.assert_called_with(
            auth_url=None, fill_in=False, identity_version='v2',
            disable_ssl_certificate_validation='true',
            ca_certs=None, password='pass', project_name='Tname',
            username='name')

    def test_set_credentials_v3(self):
        mock_function = mock.Mock()
        function2mock = 'config_tempest.credentials.auth.get_credentials'
        self.useFixture(MonkeyPatch(function2mock, mock_function))
        self.creds.username = "name"
        self.creds.password = "pass"
        self.creds.project_name = "project_name"
        self.creds.identity_version = "v3"
        self.creds.set_credentials()
        mock_function.assert_called_with(
            auth_url=None, fill_in=False, identity_version='v3',
            disable_ssl_certificate_validation='true',
            ca_certs=None, password='pass',
            username='name',
            project_name='project_name',
            domain_name='Default',
            user_domain_name='Default')

    def test_get_auth_provider_keystone_v2(self):
        # check if method returns correct method - KeystoneV2AuthProvider
        mock_function = mock.Mock()
        # mock V2Provider, if other provider is called, it fails
        func2mock = 'config_tempest.credentials.auth.KeystoneV2AuthProvider'
        self.useFixture(MonkeyPatch(func2mock, mock_function))
        resp = self.creds_v2.get_auth_provider()
        self.assertEqual(resp, mock_function())
        # check parameters of returned function
        self.creds_v2.get_auth_provider()
        mock_function.assert_called_with(self.creds_v2.tempest_creds,
                                         'http://172.16.52.151:5000/v2.0',
                                         'true', None)

    def test_get_auth_provider_keystone_v3(self):
        # check if method returns KeystoneV3AuthProvider
        # make isinstance return True
        mockIsInstance = mock.Mock(return_value=True)
        self.useFixture(MonkeyPatch('config_tempest.credentials.isinstance',
                                    mockIsInstance))
        mock_function = mock.Mock()
        # mock V3Provider, if other provider is called, it fails
        func2mock = 'config_tempest.credentials.auth.KeystoneV3AuthProvider'
        self.useFixture(MonkeyPatch(func2mock, mock_function))
        resp = self.creds.get_auth_provider()
        self.assertEqual(resp, mock_function())
        # check parameters of returned function
        self.creds.get_auth_provider()
        mock_function.assert_called_with(self.creds.tempest_creds,
                                         'http://172.16.52.151:5000/v3',
                                         'true', None)
