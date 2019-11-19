# Copyright 2016, 2018 Red Hat, Inc.
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

from six.moves import configparser
from tempest.lib import exceptions

from config_tempest.constants import LOG
from config_tempest.services.base import Service


class ObjectStorageService(Service):
    def set_extensions(self):
        if 'v3' not in self.service_url:  # it's not a v3 url
            try:
                body = self.do_get(self.service_url, top_level=True,
                                   top_level_path="info")
                body = json.loads(body)
                # Remove Swift general information from extensions list
                body.pop('swift')
                self.extensions = body.keys()
            except Exception:
                self.extensions = []
        else:
            self.extensions = []

    def list_create_roles(self, conf, client):
        try:
            roles = client.list_roles()['roles']
            for section_key in ["operator_role", "reseller_admin_role"]:
                key_value = conf.get_defaulted("object-storage", section_key)
                if key_value not in [r['name'] for r in roles]:
                    LOG.info("Creating %s role", key_value)
                    try:
                        client.create_role(name=key_value)
                    except exceptions.Conflict:
                        LOG.info("Role %s already exists", key_value)
            conf.set('object-storage', 'operator_role', 'admin')
        except exceptions.Forbidden:
            LOG.info("Roles can't be listed or created. The user doesn't have "
                     "permissions.")
            # If is not admin, we set the operator_role to Member
            # otherwise we set to admin
            conf.set('object-storage', 'operator_role', 'Member')

    def get_feature_name(self):
        return 'object-storage'

    def get_service_extension_key(self):
        return 'discoverable_apis'

    def _check_health_check(self, path):
        try:
            self.client.accounts.skip_path()
            resp, _ = self.client.accounts.get(path, {})
            return resp['status'] == '200'
        except Exception as e:
            LOG.warning('Healthcheck API not discovered giving %s', e)
            return False

    def check_service_status(self, conf):
        """Use healthcheck api to check the service status

        :type conf: TempestConf object
        """
        # Check for swift discoverability if it is False
        # check_service_status returns False
        # Else above is True, then we can check for healthcheck
        # API then we can find the service_status
        try:
            if not conf.get_bool_value(
                conf.get(
                    'object-storage-feature-enabled',
                    'discoverability')):
                return False
            return True
        except configparser.NoSectionError:
            # On swift, healthcheck is under http://.../healthcheck, while in
            # ceph is under http://.../swift/healthcheck, we check both cases
            return_value = self._check_health_check('healthcheck')
            if not return_value:
                return_value = self._check_health_check('swift/healthcheck')
            return return_value

    def set_default_tempest_options(self, conf):
        """Set default values for swift

        :type conf: TempestConf object
        """
        swift_status = self.check_service_status(conf)
        # Set roles based on service status
        if swift_status:
            self.list_create_roles(conf, self.client.roles)

    @staticmethod
    def get_service_type():
        return ['object-store']

    @staticmethod
    def get_codename():
        return 'swift'
