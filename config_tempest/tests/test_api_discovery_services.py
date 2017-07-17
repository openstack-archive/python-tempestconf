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

from config_tempest import api_discovery as api
from config_tempest.tests.base import BaseServiceTest
import mock


class TestService(BaseServiceTest):
    def setUp(self):
        super(TestService, self).setUp()
        self.Service = api.Service("ServiceName",
                                   self.FAKE_URL,
                                   self.FAKE_TOKEN,
                                   disable_ssl_validation=False)

    def _mocked_do_get(self, mock_urllib3):
        mock_http = mock_urllib3.PoolManager()
        expected_resp = mock_http.request('GET',
                                          self.FAKE_URL,
                                          self.FAKE_HEADERS)
        return expected_resp.data

    @mock.patch('config_tempest.api_discovery.urllib3')
    def test_do_get(self, mock_urllib3):
        resp = self.Service.do_get(self.FAKE_URL)
        expected_resp = self._mocked_do_get(mock_urllib3)
        self.assertEqual(resp, expected_resp)

    def test_service_headers(self):
        self.assertEqual(self.Service.headers, self.FAKE_HEADERS)


class TestVersionedService(BaseServiceTest):
    def setUp(self):
        super(TestVersionedService, self).setUp()
        self.Service = api.VersionedService("ServiceName",
                                            self.FAKE_URL,
                                            self.FAKE_TOKEN,
                                            disable_ssl_validation=False)

    def test_get_versions(self):
        expected_resp = ['v2.0', 'v2.1']
        self._fake_service_do_get_method(self.FAKE_VERSIONS)
        resp = self.Service.get_versions()
        self.assertItemsEqual(resp, expected_resp)

    def test_deserialize_versions(self):
        expected_resp = ['v2.0', 'v2.1']
        self._test_deserialize_versions(self.Service,
                                        expected_resp,
                                        self.FAKE_VERSIONS)


class TestComputeService(BaseServiceTest):
    def setUp(self):
        super(TestComputeService, self).setUp()
        self.Service = api.ComputeService("ServiceName",
                                          self.FAKE_URL,
                                          self.FAKE_TOKEN,
                                          disable_ssl_validation=False)

    def test_get_extensions(self):
        expected_resp = ['NMN', 'OS-DCF']
        self._get_extensions(self.Service, expected_resp, self.FAKE_EXTENSIONS)

    def test_get_service_class(self):
        self._test_get_service_class('compute', api.ComputeService)


class TestImageService(BaseServiceTest):
    def setUp(self):
        super(TestImageService, self).setUp()

    def test_get_service_class(self):
        self._test_get_service_class('image', api.ImageService)


class TestNetworkService(BaseServiceTest):
    def setUp(self):
        super(TestNetworkService, self).setUp()
        self.Service = api.NetworkService("ServiceName",
                                          self.FAKE_URL,
                                          self.FAKE_TOKEN,
                                          disable_ssl_validation=False)

    def test_get_extensions(self):
        expected_resp = ['NMN', 'OS-DCF']
        self._get_extensions(self.Service, expected_resp, self.FAKE_EXTENSIONS)

    def test_get_service_class(self):
        self._test_get_service_class('network', api.NetworkService)


class TestVolumeService(BaseServiceTest):
    def setUp(self):
        super(TestVolumeService, self).setUp()
        self.Service = api.VolumeService("ServiceName",
                                         self.FAKE_URL,
                                         self.FAKE_TOKEN,
                                         disable_ssl_validation=False)

    def test_get_extensions(self):
        expected_resp = ['NMN', 'OS-DCF']
        self._get_extensions(self.Service, expected_resp, self.FAKE_EXTENSIONS)

    def test_get_service_class(self):
        self._test_get_service_class('volumev3', api.VolumeService)


class TestIdentityService(BaseServiceTest):
    def setUp(self):
        super(TestIdentityService, self).setUp()
        self.Service = api.IdentityService("ServiceName",
                                           self.FAKE_URL,
                                           self.FAKE_TOKEN,
                                           disable_ssl_validation=False)

    def test_get_extensions(self):
        expected_resp = ['OS-DCF', 'NMN']
        self._get_extensions(self.Service, expected_resp,
                             self.FAKE_IDENTITY_EXTENSIONS)

    def test_deserialize_versions(self):
        expected_resp = ['v3.8', 'v2.0']
        self._test_deserialize_versions(self.Service,
                                        expected_resp,
                                        self.FAKE_IDENTITY_VERSIONS)

    def test_get_service_class(self):
        self._test_get_service_class('identity', api.IdentityService)


class TestObjectStorageService(BaseServiceTest):
    def setUp(self):
        super(TestObjectStorageService, self).setUp()
        self.Service = api.ObjectStorageService("ServiceName",
                                                self.FAKE_URL,
                                                self.FAKE_TOKEN,
                                                disable_ssl_validation=False)

    def test_get_extensions(self):
        expected_resp = ['formpost', 'ratelimit',
                         'methods', 'account_quotas']
        self._get_extensions(self.Service, expected_resp,
                             self.FAKE_STORAGE_EXTENSIONS)

    def test_get_service_class(self):
        self._test_get_service_class('object-store',
                                     api.ObjectStorageService)
