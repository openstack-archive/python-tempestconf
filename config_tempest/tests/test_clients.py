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

from fixtures import MonkeyPatch
import mock

from config_tempest.tests.base import BaseConfigTempestTest


class TestClientManager(BaseConfigTempestTest):

    def setUp(self):
        super(TestClientManager, self).setUp()
        self.conf = self._get_conf("v2.0", "v3")
        self.client = self._get_clients(self.conf)

    def test_init_manager_as_admin(self):
        mock_function = mock.Mock(return_value={"id": "my_fake_id"})
        func2mock = ('config_tempest.clients.ProjectsClient.'
                     'get_project_by_name')
        self.useFixture(MonkeyPatch(func2mock, mock_function))
        self._get_clients(self.conf, self._get_creds(self.conf, admin=True))
        # check if admin credentials were set
        admin_tenant = self.conf.get("identity", "admin_tenant_name")
        admin_password = self.conf.get("identity", "admin_password")
        self.assertEqual(self.conf.get("identity", "admin_username"), "admin")
        self.assertEqual(admin_tenant, "adminTenant")
        self.assertEqual(admin_password, "adminPass")
        # check if admin tenant id was set
        admin_tenant_id = self.conf.get("identity", "admin_tenant_id")
        self.assertEqual(admin_tenant_id, "my_fake_id")

    def test_init_manager_as_admin_using_new_auth(self):
        self.conf = self._get_alt_conf("v2.0", "v3")
        self.client = self._get_clients(self.conf)
        mock_function = mock.Mock(return_value={"id": "my_fake_id"})
        func2mock = ('config_tempest.clients.ProjectsClient'
                     '.get_project_by_name')
        self.useFixture(MonkeyPatch(func2mock, mock_function))
        self._get_clients(self.conf, self._get_creds(self.conf, admin=True))
        # check if admin credentials were set
        admin_tenant = self.conf.get("auth", "admin_project_name")
        admin_password = self.conf.get("auth", "admin_password")
        self.assertEqual(self.conf.get("auth", "admin_username"), "admin")
        self.assertEqual(admin_tenant, "adminTenant")
        self.assertEqual(admin_password, "adminPass")
        # check if admin tenant id was set
        admin_tenant_id = self.conf.get("identity", "admin_tenant_id")
        self.assertEqual(admin_tenant_id, "my_fake_id")
        use_dynamic_creds_bool = self.conf.get("auth",
                                               "use_dynamic_credentials")
        self.assertEqual(use_dynamic_creds_bool, "True")
