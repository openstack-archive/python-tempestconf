# Copyright 2019 Red Hat, Inc.
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

from six.moves import configparser

from config_tempest.constants import LOG
from config_tempest.services.base import Service


class OrchestrationService(Service):

    @staticmethod
    def get_service_type():
        return ['orchestration']

    @staticmethod
    def get_codename():
        return 'heat'

    def set_default_tempest_options(self, conf):
        try:
            uri = conf.get('identity', 'uri')
            if 'v3' not in uri:
                return
            sec = 'heat_plugin'
            # Tempest doesn't differentiate between admin or demo creds anymore
            username = conf.get('auth', 'admin_username')
            password = conf.get('auth', 'admin_password')
            conf.set(sec, 'username', username)
            conf.set(sec, 'password', password)
            conf.set(sec, 'admin_username', username)
            conf.set(sec, 'admin_password', password)
            conf.set(sec, 'project_name', conf.get('identity', 'project_name'))
            conf.set(sec, 'region', conf.get('identity', 'region'))

            conf.set(sec, 'auth_url', uri)
            v = '3' if conf.get('identity', 'auth_version') == 'v3' else '2'
            conf.set(sec, 'auth_version', v)

            domain_name = conf.get('auth', 'admin_domain_name')
            conf.set(sec, 'project_domain_name', domain_name)
            conf.set(sec, 'user_domain_name', domain_name)

            conf.set(sec, 'image_ssh_user', 'root')
            conf.set(sec, 'network_for_ssh', 'public')
            conf.set(sec, 'fixed_network_name', 'public')

            # should be set to True if using self-signed SSL certificates which
            # is a general case
            conf.set(sec, 'disable_ssl_certificate_validation', 'True')
        except configparser.NoOptionError:
            LOG.warning("Be aware that an option required for "
                        "heat_tempest_plugin cannot be set!")

    def post_configuration(self, conf, is_service):
        if conf.has_section('compute'):
            compute_options = conf.options('compute')
            if 'flavor_ref' in compute_options:
                conf.set('heat_plugin', 'minimal_instance_type',
                         conf.get('compute', 'flavor_ref'))
            if 'flavor_ref_alt' in compute_options:
                conf.set('heat_plugin', 'instance_type',
                         conf.get('compute', 'flavor_ref_alt'))
            if 'image_ref' in compute_options:
                conf.set('heat_plugin', 'minimal_image_ref',
                         conf.get('compute', 'image_ref'))
            if 'image_ref_alt' in compute_options:
                conf.set('heat_plugin', 'image_ref',
                         conf.get('compute', 'image_ref_alt'))
