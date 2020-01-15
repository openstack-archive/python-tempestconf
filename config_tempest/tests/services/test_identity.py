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

from config_tempest.services.identity import IdentityService
from config_tempest.tempest_conf import TempestConf
from config_tempest.tests.base import BaseServiceTest


class TestIdentityService(BaseServiceTest):
    def setUp(self):
        super(TestIdentityService, self).setUp()
        self.Service = IdentityService("ServiceName",
                                       "ServiceType",
                                       self.FAKE_URL + 'v2.0/',
                                       self.FAKE_TOKEN,
                                       disable_ssl_validation=False)

    def test_set_extensions(self):
        expected_resp = ['OS-DCF', 'NMN']
        self._set_get_extensions(self.Service, expected_resp,
                                 self.FAKE_IDENTITY_EXTENSIONS)
        # try with URL containing v3 version
        self.Service.service_url = self.FAKE_URL + 'v3'
        expected_resp = []
        self._set_get_extensions(self.Service, expected_resp,
                                 self.FAKE_IDENTITY_EXTENSIONS)

    def test_get_extensions(self):
        exp_resp = ['OS-INHERIT', 'OS-OAUTH1',
                    'OS-SIMPLE-CERT', 'OS-EP-FILTER']
        self.Service.extensions = exp_resp[:2]
        self.Service.extensions_v3 = exp_resp[2:]
        self.assertItemsEqual(self.Service.get_extensions(), exp_resp)

    def test_set_identity_v3_extensions(self):
        expected_resp = ['OS-INHERIT', 'OS-OAUTH1',
                         'OS-SIMPLE-CERT', 'OS-EP-FILTER']
        fake_resp = self.FakeRequestResponse(bytes_content=True)
        mocked_requests = mock.Mock()
        mocked_requests.return_value = fake_resp
        self.useFixture(MonkeyPatch('requests.get', mocked_requests))
        self.Service.service_url = self.FAKE_URL + "v3"
        fake_resp.raise_for_status = mock.Mock()
        self.Service.set_identity_v3_extensions()
        self.assertItemsEqual(self.Service.extensions_v3, expected_resp)
        self.assertItemsEqual(self.Service.get_extensions(), expected_resp)

    def test_set_get_versions(self):
        exp_resp = ['v3.8']
        self._set_get_versions(self.Service, exp_resp,
                               self.FAKE_IDENTITY_VERSIONS)

    def test_deserialize_versions(self):
        expected_resp = ['v3.8']
        self._test_deserialize_versions(self.Service,
                                        expected_resp,
                                        self.FAKE_IDENTITY_VERSIONS)
        self._test_deserialize_versions(self.Service,
                                        expected_resp,
                                        self.FAKE_IDENTITY_VERSION)
        expected_resp = ['v2.1', 'v3.8']
        # add not deprecated v2 version to FAKE_IDENTITY_VERSIONS
        v2 = [{'status': 'stable', 'id': 'v2.1'}]
        versions = self.FAKE_IDENTITY_VERSIONS['versions']['values'] + v2
        fake_versions = {'versions': {'values': versions}}
        self._test_deserialize_versions(self.Service,
                                        expected_resp,
                                        fake_versions)

    @mock.patch('config_tempest.services.identity'
                '.IdentityService.get_versions')
    def test_set_default_tempest_options(self, mock_get_versions):
        conf = TempestConf()
        mock_get_versions.return_value = ['v3.8', 'v2.0']
        self.Service.set_default_tempest_options(conf)
        self.assertEqual(
            conf.get('identity-feature-enabled',
                     'forbid_global_implied_dsr'), 'True')
