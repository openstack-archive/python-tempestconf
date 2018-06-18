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

import logging
import mock

from config_tempest.services.services import Services
from config_tempest.tests.base import BaseConfigTempestTest

# disable logging when running unit tests
logging.disable(logging.CRITICAL)


class TestEc2Service(BaseConfigTempestTest):

    FAKE_URL = "http://10.200.16.10:8774/"

    @mock.patch('config_tempest.services.services.Services.discover')
    def setUp(self, mock_discover):
        super(TestEc2Service, self).setUp()
        conf = self._get_conf('v2', 'v3')
        self.clients = self._get_clients(conf)
        self.Services = Services(self.clients, conf, self._get_creds(conf))

    def test_set_default_tempest_options(self):
        service_class = self.Services.get_service_class("ec2")
        service = service_class("ec2", self.FAKE_URL, self.clients, False)
        service.set_default_tempest_options(self.Services._conf)
        ec2_url = self.Services._conf.get("boto", "ec2_url")
        self.assertEqual(ec2_url, self.FAKE_URL)


class TestS3Service(BaseConfigTempestTest):

    FAKE_URL = "http://10.200.16.10:8774/"

    @mock.patch('config_tempest.services.services.Services.discover')
    def setUp(self, mock_discover):
        super(TestS3Service, self).setUp()
        conf = self._get_conf('v2', 'v3')
        self.clients = self._get_clients(conf)
        self.Services = Services(self.clients, conf, self._get_creds(conf))

    def test_set_default_tempest_options(self):
        service_class = self.Services.get_service_class("s3")
        service = service_class("s3", self.FAKE_URL, self.clients, False)
        service.set_default_tempest_options(self.Services._conf)
        ec2_url = self.Services._conf.get("boto", "s3_url")
        self.assertEqual(ec2_url, self.FAKE_URL)
