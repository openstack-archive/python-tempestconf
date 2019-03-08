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

import json

from config_tempest.services.base import VersionedService
from config_tempest.utils import get_base_url


class ShareService(VersionedService):

    def get_api_microversion(self):
        version_url = get_base_url(self.service_url)
        body = self.do_get(version_url)
        body = json.loads(body)
        return body

    def set_default_tempest_options(self, conf):
        if 'v2' in self.service_url:
            microversions = self.get_api_microversion()
            min_microversion = {
                version['min_version'] for version in microversions['versions']
                if version['id'] == 'v2.0'
            }

            max_microversion = {
                version['version'] for version in microversions['versions']
                if version['id'] == 'v2.0'
            }

            conf.set('share', 'min_api_microversion',
                     ''.join(min_microversion))
            conf.set('share', 'max_api_microversion',
                     ''.join(max_microversion))

    def get_unversioned_service_name(self):
        return 'share'

    @staticmethod
    def get_codename():
        return 'manila'

    def get_feature_name(self):
        return 'share'

    @staticmethod
    def get_service_name():
        return ['manila', 'manilav2']
