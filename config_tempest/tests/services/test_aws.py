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

from config_tempest.services.aws import Ec2Service
from config_tempest.services.aws import S3Service
from config_tempest.services.services import Services
from config_tempest.tests.base import BaseConfigTempestTest


class TestEc2Service(BaseConfigTempestTest):

    FAKE_URL = "http://10.200.16.10:8774/"

    @mock.patch('config_tempest.services.services.Services.discover')
    @mock.patch('config_tempest.services.services.Services.'
                'set_catalog_and_url')
    @mock.patch('config_tempest.services.services.Services.'
                'get_available_services')
    def setUp(self, mock_set_avail, mock_catalog, mock_discover):
        super(TestEc2Service, self).setUp()
        conf = self._get_conf('v2', 'v3')
        self.clients = self._get_clients(conf)
        self.Services = Services(self.clients, conf, self._get_creds(conf))

    def test_set_default_tempest_options(self):
        service = Ec2Service("ec2", "ec2", self.FAKE_URL, self.clients, False)
        service.set_default_tempest_options(self.Services._conf)
        ec2_url = self.Services._conf.get("aws", "ec2_url")
        self.assertEqual(ec2_url, self.FAKE_URL)


class TestS3Service(BaseConfigTempestTest):

    FAKE_URL = "http://10.200.16.10:8774/"

    @mock.patch('config_tempest.services.services.Services.discover')
    @mock.patch('config_tempest.services.services.Services.'
                'set_catalog_and_url')
    @mock.patch('config_tempest.services.services.Services.'
                'get_available_services')
    def setUp(self, mock_set_avail, mock_catalog, mock_discover):
        super(TestS3Service, self).setUp()
        conf = self._get_conf('v2', 'v3')
        self.clients = self._get_clients(conf)
        self.Services = Services(self.clients, conf, self._get_creds(conf))

    def test_set_default_tempest_options(self):
        service = S3Service("s3", "s3", self.FAKE_URL, self.clients, False)
        service.set_default_tempest_options(self.Services._conf)
        ec2_url = self.Services._conf.get("aws", "s3_url")
        self.assertEqual(ec2_url, self.FAKE_URL)
