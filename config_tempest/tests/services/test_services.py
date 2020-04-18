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

from config_tempest.services.services import Services
from config_tempest.tests.base import BaseConfigTempestTest
from unittest import mock


class TestServices(BaseConfigTempestTest):

    FAKE_ENTRY = {
        'endpoints': [
            {
                'region': 'my_region',
                'interface': 'public'
            },
            {
                'region': 'other_region',
                'interface': 'private'
            }
        ]
    }

    def setUp(self):
        super(TestServices, self).setUp()

    @mock.patch('config_tempest.services.services.Services.discover')
    @mock.patch('config_tempest.services.services.Services.'
                'set_catalog_and_url')
    @mock.patch('config_tempest.services.services.Services.'
                'get_available_services')
    def _create_services_instance(self, mock_avail, mock_catalog,
                                  mock_discover, v2=False):
        mock_avail.return_value = [{'name': 'my_service', 'type': 'my_type'}]
        conf = self._get_conf('v2', 'v3')
        creds = self._get_creds(conf, v2=v2)
        clients = mock.Mock()
        services = Services(clients, conf, creds)
        return services

    def test_get_endpoints_api_2(self):
        services = self._create_services_instance(v2=True)
        services._region = 'my_region'
        resp = services.get_endpoints(self.FAKE_ENTRY)
        self.assertEqual(resp, self.FAKE_ENTRY['endpoints'][0])
        services._region = 'doesnt_exist_region'
        resp = services.get_endpoints(self.FAKE_ENTRY)
        self.assertEqual(resp, self.FAKE_ENTRY['endpoints'][0])
        services._region = 'other_region'
        resp = services.get_endpoints(self.FAKE_ENTRY)
        self.assertEqual(resp, self.FAKE_ENTRY['endpoints'][1])

    def test_get_endpoints_api_3(self):
        services = self._create_services_instance()
        services._creds.api_version = 3
        services._region = 'my_region'
        resp = services.get_endpoints(self.FAKE_ENTRY)
        self.assertEqual(resp, self.FAKE_ENTRY['endpoints'][0])
        services._region = 'other_region'
        resp = services.get_endpoints(self.FAKE_ENTRY)
        self.assertEqual(resp, self.FAKE_ENTRY['endpoints'][0])

    def test_get_endpoints_no_endpoints(self):
        services = self._create_services_instance()
        resp = services.get_endpoints({'endpoints': []})
        self.assertEqual(resp, [])

    def test_parse_endpoints_empty(self):
        services = self._create_services_instance()
        services.public_url = "url"
        ep = []
        url = services.parse_endpoints(ep, "ServiceName")
        self.assertEqual("", url)

    def test_parse_endpoints(self):
        services = self._create_services_instance()
        services.public_url = "url"
        ep = {
            'url': 'http://10.0.0.107:8386/v1.1/96409a589d',
            'interface': 'public',
            'region': 'regioneOne',
        }
        url = services.parse_endpoints(ep, "ServiceName")
        self.assertEqual('http://10.0.0.107:8386/v1.1/96409a589d', url)
        ep['url'] = 'https://10.0.0.101/identity'
        auth_url = 'https://10.0.0.101:13000/v3.0'
        services._clients.auth_provider.auth_url = auth_url
        url = services.parse_endpoints(ep, 'ServiceName')
        self.assertEqual('https://10.0.0.101:13000/identity/v3', url)

    def test_parse_endpoints_not_ip_hostname(self):
        services = self._create_services_instance()
        services.public_url = "url"
        url = "https://identity-my.cloud.com:35456/v2.0"
        ep = {
            'url': url,
            'interface': 'public',
            'region': 'regioneOne',
        }
        services._clients.auth_provider.auth_url = "35456"
        url_resp = services.parse_endpoints(ep, "ServiceName")
        self.assertEqual(url, url_resp)

    def test_edit_identity_url_v3(self):
        services = self._create_services_instance()
        url_port = 'https://10.0.0.101:13000/v3.0'
        identity_url = 'https://10.0.0.101/identity'
        url_no_port = 'https://10.0.0.101/v333'
        services._clients.auth_provider.auth_url = url_port
        url = services.edit_identity_url(url_port)
        self.assertEqual(url_port, url)
        url = services.edit_identity_url(identity_url)
        self.assertEqual("https://10.0.0.101:13000/identity/v3", url)
        url = services.edit_identity_url(url_no_port)
        self.assertEqual(url_no_port, url)
        services._clients.auth_provider.auth_url = url_no_port
        url = services.edit_identity_url(identity_url)
        self.assertEqual(identity_url + "/v3", url)

    def test_edit_identity_url_v2(self):
        services = self._create_services_instance(v2=True)
        url_port = 'https://10.0.0.101:13000/v2.0'
        identity_url = 'https://10.0.0.101/identity'
        url_no_port = 'https://10.0.0.101/v2.0'
        services._clients.auth_provider.auth_url = url_port
        url = services.edit_identity_url(url_port)
        self.assertEqual(url_port, url)
        url = services.edit_identity_url(identity_url)
        self.assertEqual("https://10.0.0.101:13000/identity/v2", url)
        url = services.edit_identity_url(url_no_port)
        self.assertEqual(url_no_port, url)
        services._clients.auth_provider.auth_url = url_no_port
        url = services.edit_identity_url(identity_url)
        self.assertEqual(identity_url + "/v2", url)

    def test_get_service(self):
        services = self._create_services_instance()
        exp_resp = mock.Mock()
        exp_resp.s_type = 'my_service_type'
        services._services = [exp_resp]
        resp = services.get_service('my_service_type')
        self.assertEqual(resp, exp_resp)
        resp = services.get_service('my')
        self.assertEqual(resp, None)

    def test_is_service(self):
        services = self._create_services_instance()
        service = mock.Mock()
        service.name = 'my_service'
        service.s_type = 'my_type'
        services._services = [service]
        resp = services.is_service(name='my_service')
        self.assertEqual(resp, True)
        resp = services.is_service(name='other_service')
        self.assertEqual(resp, False)
        resp = services.is_service(**{'type': 'my_type'})
        self.assertEqual(resp, True)
        resp = services.is_service(**{'type': 'other_type'})
        self.assertEqual(resp, False)
