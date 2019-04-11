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

from config_tempest import constants as C
from config_tempest.services.base import VersionedService

from tempest.lib import exceptions


class VolumeService(VersionedService):
    def set_extensions(self):
        body = self.do_get(self.service_url + '/extensions')
        body = json.loads(body)
        self.extensions = list(map(lambda x: x['alias'], body['extensions']))

    def set_versions(self):
        url, top_level = self.no_port_cut_url()
        body = self.do_get(url, top_level=top_level)
        self.versions_body = json.loads(body)
        self.versions = self.deserialize_versions(self.versions_body)

    def set_default_tempest_options(self, conf):
        if 'v3' in self.service_url:
            m_vs = self.filter_api_microversions()
            conf.set('volume', 'min_microversion', m_vs['min_microversion'])
            conf.set('volume', 'max_microversion', m_vs['max_microversion'])

    def get_service_extension_key(self):
        return 'api_extensions'

    def get_supported_versions(self):
        return ['v2', 'v3']

    @staticmethod
    def get_codename():
        return 'cinder'

    def get_feature_name(self):
        return 'volume'

    def get_unversioned_service_name(self):
        return 'volume'

    @staticmethod
    def get_service_name():
        return ['cinderv2', 'cinderv3']

    def post_configuration(self, conf, is_service):
        # Verify if the cinder backup service is enabled
        if not is_service("volumev3"):
            C.LOG.info("No volume service found, "
                       "skipping backup service check")
            return
        try:
            params = {'binary': 'cinder-backup'}
            is_backup = self.client.list_services(**params)
        except exceptions.Forbidden:
            C.LOG.warning("User has no permissions to list services - "
                          "cinder-backup service can't be discovered.")
            return

        if is_backup:
            # We only set backup to false if the service isn't running
            # otherwise we keep the default value
            service = is_backup['services']
            if not service or service[0]['state'] == 'down':
                conf.set('volume-feature-enabled', 'backup', 'False')
