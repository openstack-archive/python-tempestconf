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

from base import VersionedService
import json


class ComputeService(VersionedService):
    def set_extensions(self):
        body = self.do_get(self.service_url + '/extensions')
        body = json.loads(body)
        self.extensions = map(lambda x: x['alias'], body['extensions'])

    def set_versions(self):
        url, top_level = self.no_port_cut_url()
        body = self.do_get(url, top_level=top_level)
        body = json.loads(body)
        self.versions = self.deserialize_versions(body)
