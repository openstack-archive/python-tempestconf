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
from fixtures import MonkeyPatch
from mock import Mock


class TestApiDiscoveryMethods(BaseServiceTest):

    FAKE_AUTH_DATA = (
        {
            'serviceCatalog': [
                {
                    'endpoints_links': [],
                    'endpoints': [{
                        'adminURL': 'http://172.16.52.151:8080/v1/AUTH_402',
                        'region': 'RegionOne',
                        'publicURL': 'http://172.16.52.151:8080/v1/AUTH_402',
                        'internalURL': 'http://172.16.52.151:8080/v1/AUTH_402',
                        'id': '22c221db6ffd4236a3fd054c60aa8fd6'
                    }],
                    'type': 'object-store',
                    'name': 'swift'
                }
            ]
        }
    )

    EXPECTED_RESP = (
        {
            'object-store':
                {
                    'extensions': 'discovered extensions',
                    'url': 'http://172.16.52.151:8080/v1/AUTH_402',
                    'versions': []
                }
        }
    )

    FAKE_AUTH_DATA_V3 = (
        {
            'serviceCatalog': [
                {
                    'endpoints_links': [],
                    'endpoints': [{
                        'adminURL': 'http://172.16.52.151:8774/v3/402',
                        'region': 'RegionOne',
                        'publicURL': 'http://172.16.52.151:8774/v3/402',
                        'internalURL': 'http://172.16.52.151:8774/v3/402',
                        'id': '01bbde4f9fb54d35badf0561a53b2bdb'
                    }],
                    'type': 'compute',
                    'name': 'nova'
                }
            ]
        }
    )

    EXPECTED_RESP_V3 = (
        {
            'compute':
            {
                'url': 'http://172.16.52.151:8774/v3/402',
                'versions': 'discovered versions'
            }
        }
    )

    def setUp(self):
        super(TestApiDiscoveryMethods, self).setUp()

    class FakeAuthProvider(object):
        def __init__(self, auth_url, auth_data):
            self.auth_url = auth_url  # 'http://172.16.52.151:5000/v2.0'
            self.auth_data = auth_data

        def get_auth(self):
            token = 'AAAAABYkehvCCJOsO2GWGqBbxk0mhH7VulICOW'
            return (token, self.auth_data)

    def _test_discover(self, url, data, function2mock,
                       mock_ret_val, expected_resp):
        provider = self.FakeAuthProvider(url, data)
        mocked_function = Mock()
        mocked_function.return_value = mock_ret_val
        self.useFixture(MonkeyPatch(function2mock, mocked_function))
        resp = api.discover(provider, "RegionOne")
        self.assertEqual(resp, expected_resp)

    def test_get_identity_v3_extensions(self):
        expected_resp = ['OS-INHERIT', 'OS-OAUTH1',
                         'OS-SIMPLE-CERT', 'OS-EP-FILTER']
        fake_resp = self.FakeRequestResponse()
        mocked_requests = Mock()
        mocked_requests.return_value = fake_resp
        self.useFixture(MonkeyPatch('requests.get', mocked_requests))
        resp = api.get_identity_v3_extensions(self.FAKE_URL + "v3")
        self.assertItemsEqual(resp, expected_resp)

    def test_discover_with_v2_url(self):
        function2mock = ('config_tempest.api_discovery.'
                         'ObjectStorageService.get_extensions')
        mock_ret_val = "discovered extensions"
        self._test_discover(self.FAKE_URL + "v2.0", self.FAKE_AUTH_DATA,
                            function2mock, mock_ret_val, self.EXPECTED_RESP)

    def test_discover_with_v3_url(self):
        function2mock = ('config_tempest.api_discovery.'
                         'ComputeService.get_versions')
        mock_ret_val = "discovered versions"
        self._test_discover(self.FAKE_URL + "v3", self.FAKE_AUTH_DATA_V3,
                            function2mock, mock_ret_val, self.EXPECTED_RESP_V3)
