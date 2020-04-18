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

from ssl import CertificateError
from unittest import mock

from fixtures import MonkeyPatch

from config_tempest.services import horizon
from config_tempest.tests.base import BaseConfigTempestTest


class TestConfigTempest(BaseConfigTempestTest):

    def setUp(self):
        super(TestConfigTempest, self).setUp()
        self.conf = self._get_conf("v2.0", "v3")

    def test_configure_horizon_ipv4(self):
        mock_function = mock.Mock(return_value=True)
        self.useFixture(MonkeyPatch('six.moves.urllib.request.urlopen',
                                    mock_function))
        horizon.configure_horizon(self.conf)
        self.assertEqual(self.conf.get('service_available', 'horizon'), "True")
        self.assertEqual(self.conf.get('dashboard', 'dashboard_url'),
                         "http://172.16.52.151/dashboard/")
        self.assertEqual(self.conf.get('dashboard', 'login_url'),
                         "http://172.16.52.151/dashboard/auth/login/")

    def test_configure_horizon_ipv6(self):
        mock_function = mock.Mock(return_value=True)
        self.useFixture(MonkeyPatch('six.moves.urllib.request.urlopen',
                                    mock_function))
        self.conf.set('identity', 'uri', 'http://[::1]:5000/v3', priority=True)
        horizon.configure_horizon(self.conf)
        self.assertEqual(self.conf.get('service_available', 'horizon'), "True")
        self.assertEqual(self.conf.get('dashboard', 'dashboard_url'),
                         "http://[::1]/dashboard/")
        self.assertEqual(self.conf.get('dashboard', 'login_url'),
                         "http://[::1]/dashboard/auth/login/")

    def test_configure_horizon_certificate_error(self):
        mock_function = mock.Mock(return_value=True)
        mock_function.side_effect = CertificateError
        self.useFixture(MonkeyPatch('six.moves.urllib.request.urlopen',
                                    mock_function))
        horizon.configure_horizon(self.conf)
        self.assertEqual(self.conf.get('service_available', 'horizon'),
                         "False")
        self.assertFalse(self.conf.has_section('dashboard'))
