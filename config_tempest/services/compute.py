# Copyright 2013 Red Hat, Inc.
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

from tempest.lib import exceptions

from config_tempest import constants as C
from config_tempest.services.base import VersionedService


class ComputeService(VersionedService):
    def set_versions(self):
        url, top_level = self.no_port_cut_url()
        body = self.do_get(url, top_level=top_level)
        self.versions_body = json.loads(body)
        self.versions = self.deserialize_versions(self.versions_body)

    def set_default_tempest_options(self, conf):
        conf.set('compute-feature-enabled', 'console_output', 'True')
        num_compute = self._get_number_of_hosts()
        # set min_compute_nodes to enable migration tests in env
        # with multiple compute nodes
        conf.set('compute', 'min_compute_nodes', str(num_compute))
        # Resize only works if it has at least 2 compute nodes
        # or if nova has the option allow_resize_to_same_host
        # set to true. Unfortunately we can't get this info from
        # nova api, so we only set it when we know there's 2
        # compute nodes
        if num_compute >= 2:
            conf.set('compute-feature-enabled', 'resize', 'True')
        # set microversions
        m_versions = self.filter_api_microversions()
        conf.set('compute', 'min_microversion', m_versions['min_microversion'])
        conf.set('compute', 'max_microversion', m_versions['max_microversion'])

    def _get_number_of_hosts(self):
        # Right now the client returned is hosts, in the future
        # change it to a dict, and get the client as requested
        try:
            hosts = self.client.list_hosts()['hosts']
            compute_hosts = [h for h in hosts if h['service'] == 'compute']
            return len(compute_hosts)
        except exceptions.Forbidden:
            C.LOG.info('Can not retrieve hosts, user are not allowed')
            return 1

    def post_configuration(self, conf, is_service):
        conf.set('compute-feature-enabled', 'attach_encrypted_volume',
                 str(is_service(**{'type': 'key-manager'})))

    @staticmethod
    def get_service_type():
        return ['compute']

    @staticmethod
    def get_codename():
        return 'nova'
