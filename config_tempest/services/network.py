# Copyright 2013, 2016 Red Hat, Inc.
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

import json

from base import VersionedService
from config_tempest.constants import LOG


class NetworkService(VersionedService):
    def set_extensions(self):
        body = self.do_get(self.service_url + '/v2.0/extensions.json')
        body = json.loads(body)
        self.extensions = map(lambda x: x['alias'], body['extensions'])

    def create_tempest_networks(self, has_neutron, conf, network_id):
        LOG.info("Setting up network")
        LOG.debug("Is neutron present: {0}".format(has_neutron))
        if has_neutron:
            self.client = self.client.get_neutron_client()
            self.create_tempest_networks_neutron(conf, network_id)
        else:
            self.client = self.client.get_nova_net_client()
            self.create_tempest_networks_nova(conf)

    def create_tempest_networks_neutron(self, conf, public_network_id):
        self._public_network_name = None
        self._public_network_id = public_network_id
        # if user supplied the network we should use
        if public_network_id:
            self._supplied_network()
        # no network id provided, try to auto discover a public network
        else:
            self._discover_network()
        if self._public_network_id is not None:
            conf.set('network', 'public_network_id', self._public_network_id)
        if self._public_network_name is not None:
            conf.set('network', 'floating_network_name',
                     self._public_network_name)

    def _supplied_network(self):
        LOG.info("Looking for existing network id: {0}"
                 "".format(self._public_network_id))
        # check if network exists
        network_list = self.client.list_networks()
        for network in network_list['networks']:
            if network['id'] == self._public_network_id:
                self._public_network_name = network['name']
                break
        else:
            raise ValueError('provided network id: {0} was not found.'
                             ''.format(self._public_network_id))

    def _discover_network(self):
        LOG.info("No network supplied, trying auto discover for network")
        network_list = self.client.list_networks()
        for network in network_list['networks']:
            if network['router:external'] and network['subnets']:
                LOG.info("Found network, using: {0}".format(network['id']))
                self._public_network_id = network['id']
                self._public_network_name = network['name']
                break

        # Couldn't find an existing external network
        else:
            LOG.error("No external networks found. "
                      "Please note that any test that relies on external "
                      "connectivity would most likely fail.")

    def create_tempest_networks_nova(self, conf):
        networks = self.client.list_networks()
        if networks:
            label = networks['networks'][0]['label']
            if label:
                conf.set('compute', 'fixed_network_name', label)
            else:
                raise Exception('fixed_network_name could not be '
                                'discovered and must be specified')