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

import mock

from config_tempest import constants as C
from config_tempest.services.object_storage import ObjectStorageService
from config_tempest import tempest_conf
from config_tempest.tests.base import BaseServiceTest


class TestObjectStorageService(BaseServiceTest):
    def setUp(self):
        super(TestObjectStorageService, self).setUp()
        self.Service = ObjectStorageService("ServiceName",
                                            self.FAKE_URL,
                                            self.FAKE_TOKEN,
                                            disable_ssl_validation=False)

    def test_set_get_extensions(self):
        expected_resp = ['formpost', 'ratelimit',
                         'methods', 'account_quotas']
        self._fake_service_do_get_method(self.FAKE_STORAGE_EXTENSIONS)
        self.Service.set_extensions(object_store_discovery=True)
        self.assertItemsEqual(self.Service.extensions, expected_resp)
        self.assertItemsEqual(self.Service.get_extensions(), expected_resp)
        self.Service.set_extensions()
        self.assertItemsEqual(self.Service.extensions, [])
        self.assertItemsEqual(self.Service.get_extensions(), [])

    def test_list_create_roles(self):
        conf = tempest_conf.TempestConf()
        # TODO(mkopec) remove reading of default file when it's removed
        conf.read(C.DEFAULTS_FILE)
        client = mock.Mock()
        return_mock = mock.Mock(return_value=self.FAKE_ROLES)
        client.list_roles = return_mock
        client.create_role = mock.Mock()
        self.Service.list_create_roles(conf, client)
        self.assertEqual(conf.get('object-storage', 'reseller_admin'),
                         'ResellerAdmin')
        # Member role is inherited from tempest.config
        self.assertEqual(conf.get('object-storage', 'operator_role'),
                         'Member')
        self.assertTrue(client.create_role.called)
