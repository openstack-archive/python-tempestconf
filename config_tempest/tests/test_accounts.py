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

import os
from unittest import mock

from config_tempest import accounts
from config_tempest import main
from config_tempest.tests.base import BaseConfigTempestTest


class TestAccounts(BaseConfigTempestTest):
    """Accounts test class

    Tests for create_accounts_file and write_accounts_file methods.
    """

    def setUp(self):
        super(TestAccounts, self).setUp()
        self.conf = self._get_conf("v2.0", "v3")

    @mock.patch('config_tempest.accounts.write_accounts_file')
    def test_create_accounts_file(self, mock_write):
        path = "./etc/accounts.yaml"
        main.set_options(self.conf, None, False, "", accounts_path=path)
        # credentials under auth section
        accounts.create_accounts_file(True, path, self.conf)
        mock_write.assert_called_with(path, "admin", "adminPass",
                                      "adminProject")
        self.assertEqual(self.conf.get("auth", "test_accounts_file"),
                         os.path.abspath(path))

        # credentials under identity section
        accounts.create_accounts_file(False, path, self.conf)
        mock_write.assert_called_with(path, "demo", "secret", "demo")
        self.assertEqual(self.conf.get("auth", "test_accounts_file"),
                         os.path.abspath(path))
