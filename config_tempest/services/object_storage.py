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

from base import Service
from config_tempest.constants import LOG
from tempest.lib import exceptions


class ObjectStorageService(Service):
    def set_extensions(self, object_store_discovery=False):
        if not object_store_discovery:
            self.extensions = []
        elif 'v3' not in self.service_url:  # it's not a v3 url
            body = self.do_get(self.service_url, top_level=True,
                               top_level_path="info")
            body = json.loads(body)
            # Remove Swift general information from extensions list
            body.pop('swift')
            self.extensions = body.keys()

    def list_create_roles(self, conf, client):
        try:
            roles = client.list_roles()['roles']
        except exceptions.Forbidden:
            LOG.info("Roles can't be listed - the user needs permissions.")
            return

        for section_key in ["operator_role", "reseller_admin"]:
            key_value = conf.get_defaulted("object-storage", section_key)
            if key_value not in [r['name'] for r in roles]:
                LOG.info("Creating %s role", key_value)
                client.create_role(name=key_value)

            conf.set("object-storage", section_key, key_value)
