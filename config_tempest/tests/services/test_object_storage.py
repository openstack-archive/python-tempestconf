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

from config_tempest import main
from config_tempest.services.object_storage import ObjectStorageService
from config_tempest import tempest_conf
from config_tempest.tests.base import BaseServiceTest


class TestObjectStorageService(BaseServiceTest):
    def setUp(self):
        super(TestObjectStorageService, self).setUp()
        self.Service = ObjectStorageService("ServiceName",
                                            "ServiceType",
                                            self.FAKE_URL,
                                            self.FAKE_TOKEN,
                                            disable_ssl_validation=False)
        self.Service.conf = tempest_conf.TempestConf()

    def test_set_get_extensions(self):
        expected_resp = ['formpost', 'ratelimit',
                         'methods', 'account_quotas']
        self._fake_service_do_get_method(self.FAKE_STORAGE_EXTENSIONS)
        self.Service.set_extensions()
        self.assertItemsEqual(self.Service.extensions, expected_resp)
        self.assertItemsEqual(self.Service.get_extensions(), expected_resp)

    def test_set_get_extensions_empty(self):
        self.Service.service_url = self.FAKE_URL + 'v3'
        self.Service.set_extensions()
        self.assertItemsEqual(self.Service.extensions, [])
        self.assertItemsEqual(self.Service.get_extensions(), [])

    def test_list_create_roles(self):
        conf = self.Service.conf
        # load default values
        main.load_basic_defaults(self.Service.conf)
        client = mock.Mock()
        return_mock = mock.Mock(return_value=self.FAKE_ROLES)
        client.list_roles = return_mock
        client.create_role = mock.Mock()
        self.Service.list_create_roles(conf, client)
        self.assertEqual(conf.get('object-storage', 'reseller_admin_role'),
                         'ResellerAdmin')
        self.assertEqual(conf.get('object-storage', 'operator_role'),
                         'admin')
        self.assertTrue(client.create_role.called)

    def test_check_service_status_discover(self):
        self.Service.client = mock.Mock()
        self.Service.client.accounts = mock.Mock()
        return_mock = mock.Mock(return_value=self.FAKE_ACCOUNTS)
        self.Service.client.accounts.skip_check = mock.Mock()
        self.Service.client.accounts.get = return_mock
        resp = self.Service.check_service_status(self.Service.conf)
        self.assertTrue(resp)

    def test_check_service_status(self):
        # discoverability set to False (e.g. via overrides)
        self.Service.conf.set('object-storage-feature-enabled',
                              'discoverability',
                              str(False))
        resp = self.Service.check_service_status(self.Service.conf)
        self.assertFalse(resp)
        # discoverability set to True (e.g. via overrides)
        self.Service.conf.set('object-storage-feature-enabled',
                              'discoverability',
                              str(True))
        resp = self.Service.check_service_status(self.Service.conf)
        self.assertTrue(resp)
