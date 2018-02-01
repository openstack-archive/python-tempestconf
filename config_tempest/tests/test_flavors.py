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

from fixtures import MonkeyPatch
import mock

from config_tempest.flavors import Flavors
from config_tempest.tests.base import BaseConfigTempestTest


class TestFlavors(BaseConfigTempestTest):
    """Flavors test class

    Tests for create_tempest_flavors and find_or_create_flavor methods.
    """

    CLIENT_MOCK = 'tempest.lib.services.compute.flavors_client.FlavorsClient'
    FLAVORS_LIST = [
        {"id": "Fakeid", "name": "Name"},
        {"id": "MyFakeID", "name": "MyID"}
    ]

    def setUp(self):
        super(TestFlavors, self).setUp()
        self.conf = self._get_conf("v2.0", "v3")
        self.client = self._get_clients(self.conf).flavors
        self.Service = Flavors(self.client, True, self.conf)

    def _mock_create_tempest_flavor(self, mock_function):
        func2mock = 'config_tempest.flavors.Flavors.find_or_create_flavor'
        self.useFixture(MonkeyPatch(func2mock, mock_function))
        self.Service.create_tempest_flavors()

    def _mock_find_or_create_flavor(self, return_value, func2mock, flavor_name,
                                    expected_resp, allow_creation=False,
                                    flavor_id=None):
        self.Service.allow_creation = allow_creation
        mock_function = mock.Mock(return_value=return_value)
        self.useFixture(MonkeyPatch(self.CLIENT_MOCK + func2mock,
                                    mock_function))
        resp = self.Service.find_or_create_flavor(flavor_id=flavor_id,
                                                  flavor_name=flavor_name)
        self.assertEqual(resp, expected_resp)

    def test_create_tempest_flavors(self):
        mock_function = mock.Mock(return_value="FakeID")
        self._mock_create_tempest_flavor(mock_function)
        self.assertEqual(self.conf.get('compute', 'flavor_ref'), "FakeID")
        self.assertEqual(self.conf.get('compute', 'flavor_ref_alt'), "FakeID")
        calls = [mock.call(None, 'm1.nano', ram=64),
                 mock.call(None, 'm1.micro', ram=128)]
        mock_function.assert_has_calls(calls, any_order=True)

    def test_create_tempest_flavors_overwrite(self):
        mock_function = mock.Mock(return_value="FakeID")
        self.conf.set('compute', 'flavor_ref', "FAKE_ID")
        self.conf.set('compute', 'flavor_ref_alt', "FAKE_ID")
        self._mock_create_tempest_flavor(mock_function)
        calls = [mock.call("FAKE_ID", 'm1.nano', ram=64),
                 mock.call("FAKE_ID", 'm1.micro', ram=128)]
        mock_function.assert_has_calls(calls, any_order=True)

    def test_create_flavor_not_allowed(self):
        # mock list_flavors() to return empty list
        self.Service.allow_creation = False
        mock_function = mock.Mock(return_value={"flavors": []})
        self.useFixture(MonkeyPatch(self.CLIENT_MOCK + '.list_flavors',
                                    mock_function))
        exc = Exception
        self.assertRaises(exc,
                          self.Service.find_or_create_flavor,
                          flavor_id="id",
                          flavor_name="name")

    def test_create_flavor(self):
        return_value = {"flavor": {"id": "MyFakeID", "name": "MyID"}}
        # mock list_flavors() to return empty list
        mock_function = mock.Mock(return_value={"flavors": []})
        self.useFixture(MonkeyPatch(self.CLIENT_MOCK + '.list_flavors',
                                    mock_function))
        self._mock_find_or_create_flavor(return_value=return_value,
                                         func2mock='.create_flavor',
                                         flavor_name="MyID",
                                         expected_resp="MyFakeID",
                                         allow_creation=True)

    def test_find_flavor_by_id(self):
        return_value = {"flavors": self.FLAVORS_LIST}
        self._mock_find_or_create_flavor(return_value=return_value,
                                         func2mock='.list_flavors',
                                         flavor_id="MyFakeID",
                                         flavor_name=None,
                                         expected_resp="MyFakeID")

    def test_find_flavor_by_name(self):
        return_value = {"flavors": self.FLAVORS_LIST}
        self._mock_find_or_create_flavor(return_value=return_value,
                                         func2mock='.list_flavors',
                                         flavor_name="MyID",
                                         expected_resp="MyFakeID")
