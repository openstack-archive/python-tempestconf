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

from config_tempest.services.base import Service
from config_tempest.services.base import VersionedService
from config_tempest.tests.base import BaseServiceTest


class TestService(BaseServiceTest):
    def setUp(self):
        super(TestService, self).setUp()
        self.Service = Service("ServiceName",
                               "ServiceType",
                               self.FAKE_URL,
                               self.FAKE_TOKEN,
                               disable_ssl_validation=False)

    def _mocked_do_get(self, mock_urllib3):
        mock_http = mock_urllib3.PoolManager()
        expected_resp = mock_http.request('GET',
                                          self.FAKE_URL,
                                          self.FAKE_HEADERS)
        return expected_resp.data.decode('utf-8')

    @mock.patch('config_tempest.services.base.urllib3')
    def test_do_get(self, mock_urllib3):
        mock_http = mock.Mock()
        mock_r = mock.Mock()
        mock_r.status = 200
        mock_http.request.return_value = mock_r
        mock_urllib3.PoolManager.return_value = mock_http

        resp = self.Service.do_get(self.FAKE_URL)
        expected_resp = self._mocked_do_get(mock_urllib3)
        self.assertEqual(resp, expected_resp)

    def test_service_properties(self):
        self.assertEqual(self.Service.name, "ServiceName")
        self.assertEqual(self.Service.service_url, self.FAKE_URL)
        self.assertEqual(self.Service.headers, self.FAKE_HEADERS)
        self.assertEqual(self.Service.disable_ssl_validation, False)
        self.assertEqual(self.Service.client, None)
        self.assertEqual(self.Service.extensions, [])
        self.assertEqual(self.Service.versions, [])

    def test_set_extensions(self):
        self.Service.extensions = ['ext']
        self.Service.set_extensions()
        self.assertEqual(self.Service.extensions, [])

    def test_set_versions(self):
        self.Service.versions = ['ver']
        self.Service.set_versions()
        self.assertEqual(self.Service.versions, [])

    def test_get_extensions(self):
        self.Service.extensions = ['ext']
        self.assertEqual(self.Service.get_extensions(), ['ext'])

    def test_get_versions(self):
        self.Service.versions = ['ver']
        self.assertEqual(self.Service.get_versions(), ['ver'])


class TestVersionedService(BaseServiceTest):
    def setUp(self):
        super(TestVersionedService, self).setUp()
        self.Service = VersionedService("ServiceName",
                                        "ServiceType",
                                        self.FAKE_URL,
                                        self.FAKE_TOKEN,
                                        disable_ssl_validation=False)

    def test_set_get_versions(self):
        expected_resp = ['v2.0', 'v2.1']
        self._fake_service_do_get_method(self.FAKE_VERSIONS)
        self.Service.set_versions()
        resp = self.Service.get_versions()
        self.assertItemsEqual(resp, expected_resp)
        self.assertItemsEqual(self.Service.versions, expected_resp)

    def test_deserialize_versions(self):
        expected_resp = ['v2.0', 'v2.1']
        self._test_deserialize_versions(self.Service,
                                        expected_resp,
                                        self.FAKE_VERSIONS)

    def test_no_port_cut_url(self):
        resp = self.Service.no_port_cut_url()
        self.assertEqual(resp, (self.FAKE_URL, True))
        url = "http://10.200.16.10"
        self.Service.service_url = url
        resp = self.Service.no_port_cut_url()
        self.assertEqual(resp, (self.Service.service_url, False))
        self.Service.service_url = url + "/v3/cut/it/off"
        resp = self.Service.no_port_cut_url()
        self.assertEqual(resp, (url + '/', False))
