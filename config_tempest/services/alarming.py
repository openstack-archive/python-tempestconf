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

from config_tempest.services.base import Service


class AlarmingService(Service):

    def set_availability(self, conf, available):
        # TODO(arxcruz): Remove this once/if we get the following reviews
        # merged in all branches supported by tempestconf, or once/if
        # tempestconf do not support anymore the OpenStack release where
        # those patches are not available.
        # https://review.openstack.org/#/c/492526/
        # https://review.openstack.org/#/c/492525/
        conf.set('service_available', 'aodh', str(available))
        conf.set('service_available', 'aodh_plugin', str(available))

    @staticmethod
    def get_service_name():
        return ['aodh']
