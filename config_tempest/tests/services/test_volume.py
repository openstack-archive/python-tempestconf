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

from config_tempest.services import volume
from config_tempest.tempest_conf import TempestConf
from config_tempest.tests.base import BaseServiceTest


class TestVolumeService(BaseServiceTest):
    def setUp(self):
        super(TestVolumeService, self).setUp()
        self.Service = volume.VolumeService("ServiceName",
                                            "ServiceType",
                                            self.FAKE_URL,
                                            self.FAKE_TOKEN,
                                            disable_ssl_validation=False)
        self.conf = TempestConf()

    def test_set_get_extensions(self):
        exp_resp = ['NMN', 'OS-DCF']
        self._set_get_extensions(self.Service, exp_resp, self.FAKE_EXTENSIONS)

    def test_set_get_versions(self):
        exp_resp = ['v2.0', 'v2.1']
        self._set_get_versions(self.Service, exp_resp, self.FAKE_VERSIONS)

    @mock.patch('config_tempest.services.services.Services.is_service')
    @mock.patch('config_tempest.services.volume.C.LOG')
    def test_post_configuration_no_volume(self, mock_logging, mock_is_service):
        mock_is_service.return_value = False
        self.Service.post_configuration(self.conf, mock_is_service)
        self.assertTrue(mock_logging.info.called)
        self.assertEqual(self.conf.get('volume-feature-enabled', 'backup'),
                         'False')

    @mock.patch('config_tempest.services.services.Services.is_service')
    def test_post_configuration_state_down(self, mock_is_service):
        client_service_mock = self.FakeServiceClient(services={
            'services': [
                {
                    "state": "down"
                }
            ]
        })
        self.Service.client = client_service_mock
        mock_is_service.return_value = True
        self.Service.post_configuration(self.conf, mock_is_service)
        self.assertEqual(self.conf.get('volume-feature-enabled',
                         'backup'), 'False')

    @mock.patch('config_tempest.services.services.Services.is_service')
    def test_post_configuration_no_service(self, mock_is_service):
        client_service_mock = self.FakeServiceClient(services={
            'services': []
        })
        self.Service.client = client_service_mock
        mock_is_service.return_value = True
        self.Service.post_configuration(self.conf, mock_is_service)
        self.assertEqual(self.conf.get('volume-feature-enabled',
                         'backup'), 'False')
