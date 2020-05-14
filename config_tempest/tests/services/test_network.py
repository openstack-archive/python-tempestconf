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

from config_tempest.services.network import NetworkService
from config_tempest.tempest_conf import TempestConf
from config_tempest.tests.base import BaseServiceTest


class TestNetworkService(BaseServiceTest):

    FAKE_NETWORK_LIST = {
        'networks': [{
            'provider:physical_network': None,
            'id': '1ea533d7-4c65-4f25',
            'router:external': True,
            'availability_zone_hints': [],
            'availability_zones': [],
            'ipv4_address_scope': None,
            'status': 'ACTIVE',
            'subnets': ['fake_subnet'],
            'label': 'my_fake_label',
            'name': 'tempest-network',
            'admin_state_up': True,
        }]
    }

    def setUp(self):
        super(TestNetworkService, self).setUp()
        self.conf = TempestConf()
        self.Service = NetworkService("ServiceName",
                                      "ServiceType",
                                      self.FAKE_URL,
                                      self.FAKE_TOKEN,
                                      disable_ssl_validation=False)
        self.Service.client = self.FakeServiceClient()

    def test_set_get_extensions(self):
        exp_resp = ['NMN', 'OS-DCF']
        self._set_get_extensions(self.Service, exp_resp, self.FAKE_EXTENSIONS)

    def test_tempest_network_id_not_found(self):
        return_mock = mock.Mock(return_value={"networks": []})
        self.Service.client.list_networks = return_mock
        self.Service._public_network_id = "doesn't_exist"
        self.assertRaises(ValueError,
                          self.Service._supplied_network)

    def test_create_network_id_supplied_by_user(self):
        return_mock = mock.Mock(return_value=self.FAKE_NETWORK_LIST)
        self.Service.client.list_networks = return_mock
        self.Service._public_network_id = '1ea533d7-4c65-4f25'
        self.Service._supplied_network()
        self.assertEqual(self.Service._public_network_name, 'tempest-network')

    def test_create_network_auto_discover(self):
        return_mock = mock.Mock(return_value=self.FAKE_NETWORK_LIST)
        self.Service.client.list_networks = return_mock
        self.Service._discover_network()
        self.assertEqual(self.Service._public_network_id, '1ea533d7-4c65-4f25')
        self.assertEqual(self.Service._public_network_name, 'tempest-network')

    @mock.patch('config_tempest.services.network.LOG')
    def test_create_network_auto_discover_not_found(self, mock_logging):
        # delete subnets => network will not be found
        self.FAKE_NETWORK_LIST['networks'][0]['subnets'] = []
        return_mock = mock.Mock(return_value=self.FAKE_NETWORK_LIST)
        self.Service.client.list_networks = return_mock
        self.Service._discover_network()
        # check if LOG.error was called
        self.assertTrue(mock_logging.error.called)
