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

from config_tempest import constants as C
from config_tempest.services.base import VersionedService

from tempest.lib import exceptions


class ShareService(VersionedService):

    def get_share_pools(self):
        body = self.do_get(self.service_url + '/scheduler-stats/pools')
        body = json.loads(body)
        return body

    def set_default_tempest_options(self, conf):
        if 'v2' in self.service_url:
            m_vs = self.filter_api_microversions()
            conf.set('share', 'min_api_microversion', m_vs['min_microversion'])
            conf.set('share', 'max_api_microversion', m_vs['max_microversion'])

        try:
            pools = self.get_share_pools()['pools']
        except exceptions.Forbidden:
            C.LOG.warning("User has no permissions to list back-end storage "
                          "pools - storage back-ends can't be discovered.")
            return
        if pools:
            backends = [
                pool['backend'] for pool in pools
            ]
            conf.set('share', 'backend_names', ','.join(backends))
            if len(backends) > 1:
                conf.set('share', 'multi_backend', True)

    def get_unversioned_service_type(self):
        return 'share'

    @staticmethod
    def get_codename():
        return 'manila'

    def get_feature_name(self):
        return 'share'

    @staticmethod
    def get_service_type():
        return ['share', 'sharev2']
