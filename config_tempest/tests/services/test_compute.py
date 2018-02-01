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

from config_tempest.services.compute import ComputeService
from config_tempest.tests.base import BaseServiceTest


class TestComputeService(BaseServiceTest):
    def setUp(self):
        super(TestComputeService, self).setUp()
        self.Service = ComputeService("ServiceName",
                                      self.FAKE_URL,
                                      self.FAKE_TOKEN,
                                      disable_ssl_validation=False)

    def test_set_get_extensions(self):
        exp_resp = ['NMN', 'OS-DCF']
        self._set_get_extensions(self.Service, exp_resp, self.FAKE_EXTENSIONS)

    def test_set_get_versions(self):
        exp_resp = ['v2.0', 'v2.1']
        self._set_get_versions(self.Service, exp_resp, self.FAKE_VERSIONS)
