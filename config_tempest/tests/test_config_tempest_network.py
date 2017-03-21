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

from config_tempest import config_tempest as tool
from config_tempest.tests.base import BaseConfigTempestTest
from fixtures import MonkeyPatch
import mock


class TestCreateTempestNetworks(BaseConfigTempestTest):

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

    NEUTRON_CLIENT_MOCK = ('tempest.lib.services.network.'
                           'networks_client.NetworksClient')
    NOVA_CLIENT_MOCK = ('tempest.lib.services.compute.'
                        'networks_client.NetworksClient')

    def setUp(self):
        super(TestCreateTempestNetworks, self).setUp()
        self.conf = self._get_conf("v2.0", "v3")
        self.clients = self._get_clients(self.conf)

    def _mock_list_networks(self, client, client_mock, return_value):
        mock_function = mock.Mock(return_value=return_value)
        client_mock = client_mock + '.list_networks'
        self.useFixture(MonkeyPatch(client_mock, mock_function))

    def test_tempest_network_id_not_found(self):
        neutron_client = self.clients.get_neutron_client()
        self._mock_list_networks(neutron_client,
                                 self.NEUTRON_CLIENT_MOCK,
                                 return_value={"networks": []})
        self.assertRaises(ValueError,
                          tool.create_tempest_networks,
                          clients=self.clients,
                          conf=self.conf,
                          has_neutron=True,
                          public_network_id="doesn't_exist")

    def test_create_network_id_supplied_by_user(self):
        neutron_client = self.clients.get_neutron_client()
        self._mock_list_networks(neutron_client,
                                 self.NEUTRON_CLIENT_MOCK,
                                 return_value=self.FAKE_NETWORK_LIST)
        tool.create_tempest_networks(clients=self.clients,
                                     conf=self.conf,
                                     has_neutron=True,
                                     public_network_id='1ea533d7-4c65-4f25')
        self.assertEqual(self.conf.get('network', 'public_network_id'),
                         '1ea533d7-4c65-4f25')

    def test_create_network_auto_discover(self):
        neutron_client = self.clients.get_neutron_client()
        self._mock_list_networks(neutron_client,
                                 self.NEUTRON_CLIENT_MOCK,
                                 return_value=self.FAKE_NETWORK_LIST)
        tool.create_tempest_networks(clients=self.clients,
                                     conf=self.conf,
                                     has_neutron=True,
                                     public_network_id=None)
        self.assertEqual(self.conf.get('network', 'public_network_id'),
                         '1ea533d7-4c65-4f25')
        self.assertEqual(self.conf.get('network', 'floating_network_name'),
                         'tempest-network')

    @mock.patch('config_tempest.config_tempest.LOG')
    def test_create_network_auto_discover_not_found(self, mock_logging):
        neutron_client = self.clients.get_neutron_client()
        # delete subnets => network will not be found
        self.FAKE_NETWORK_LIST['networks'][0]['subnets'] = []
        self._mock_list_networks(neutron_client,
                                 self.NEUTRON_CLIENT_MOCK,
                                 return_value=self.FAKE_NETWORK_LIST)
        tool.create_tempest_networks(clients=self.clients,
                                     conf=self.conf,
                                     has_neutron=True,
                                     public_network_id=None)
        # check if LOG.error was called
        self.assertTrue(mock_logging.error.called)

    def test_network_not_discovered(self):
        exception = Exception
        nova_client = self.clients.get_nova_net_client()
        self._mock_list_networks(nova_client,
                                 self.NOVA_CLIENT_MOCK,
                                 return_value=False)
        self.assertRaises(exception,
                          tool.create_tempest_networks,
                          clients=self.clients,
                          conf=self.conf,
                          has_neutron=False,
                          public_network_id=None)

    def test_create_fixed_network(self):
        nova_client = self.clients.get_nova_net_client()
        self._mock_list_networks(nova_client,
                                 self.NOVA_CLIENT_MOCK,
                                 return_value=self.FAKE_NETWORK_LIST)
        tool.create_tempest_networks(clients=self.clients,
                                     conf=self.conf,
                                     has_neutron=False,
                                     public_network_id=None)
        self.assertEqual(self.conf.get('compute', 'fixed_network_name'),
                         'my_fake_label')
