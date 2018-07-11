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
import logging
import mock

from config_tempest.flavors import Flavors
from config_tempest.tests.base import BaseConfigTempestTest

# disable logging when running unit tests
logging.disable(logging.CRITICAL)


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
        return_value = {"flavors": [{"id": "MyFakeID", "name": "MyID"}]}
        mock_function = mock.Mock(return_value=return_value)
        self.useFixture(MonkeyPatch(self.CLIENT_MOCK + '.list_flavors',
                                    mock_function))
        self.Service = Flavors(self.client, True, self.conf)

    def test_create_tempest_flavors(self):
        self.Service.flavor_list = []
        mock_function = mock.Mock(return_value="FakeID")
        func2mock = 'config_tempest.flavors.Flavors.create_flavor'
        self.useFixture(MonkeyPatch(func2mock, mock_function))
        self.Service.create_tempest_flavors()
        self.assertEqual(self.conf.get('compute', 'flavor_ref'), "FakeID")
        self.assertEqual(self.conf.get('compute', 'flavor_ref_alt'), "FakeID")
        calls = [mock.call('m1.nano', ram=64),
                 mock.call('m1.micro', ram=128)]
        mock_function.assert_has_calls(calls, any_order=True)

    def check_call_of_discover_smallest_flavor(self):
        self.Service.flavor_list = [{'id': 'FAKE', 'name': 'Fake_flavor'},
                                    {'id': 'FAKE_1', 'name': 'Fake_flavor_1'}]
        self.Service.allow_creation = False
        func2mock = 'config_tempest.flavors.Flavors.discover_smallest_flavor'
        mock_function = mock.Mock()
        self.useFixture(MonkeyPatch(func2mock, mock_function))
        self.Service.create_flavor('nano')
        calls = [mock.call('nano')]
        mock_function.assert_has_calls(calls, any_order=True)

    def test_create_tempest_flavors_overwrite_flavor_ref_not_exist(self):
        self.conf.set('compute', 'flavor_ref', "FAKE_ID")
        try:
            self.Service.create_tempest_flavors()
        except Exception:
            return
        # it should have ended in the except block above
        self.assertTrue(False)

    def test_create_tempest_flavors_overwrite_flavor_ref_alt_not_exist(self):
        self.Service.flavor_list = [{'id': 'FAKE', 'name': 'Fake_flavor'}]
        self.conf.set('compute', 'flavor_ref', 'FAKE')
        self.conf.set('compute', 'flavor_ref_alt', 'FAKE_ID')
        try:
            self.Service.create_tempest_flavors()
        except Exception:
            self.assertEqual(self.conf.get('compute', 'flavor_ref'), 'FAKE')
            return
        # it should have ended in the except block above
        self.assertTrue(False)

    def test_create_flavor_not_allowed(self):
        # mock list_flavors() to return empty list
        self.Service.allow_creation = False
        self.Service.flavor_list = []
        try:
            self.Service.create_flavor('name')
        except Exception:
            return
        # it should have ended in the except block above
        self.assertTrue(False)

        # not enough flavors found
        self.Service.flavor_list = [{'id': 'FAKE', 'name': 'fake_name'}]
        try:
            self.Service.create_flavor('name')
        except Exception:
            return
        # it should have ended in the except block above
        self.assertTrue(False)

    def test_create_flavor(self):
        return_value = {"flavor": {"id": "MyFakeID", "name": "MyID"}}
        self.Service.flavor_list = []
        mock_function = mock.Mock(return_value=return_value)
        self.useFixture(MonkeyPatch(self.CLIENT_MOCK + '.create_flavor',
                                    mock_function))
        resp = self.Service.create_flavor(flavor_name="MyID")
        self.assertEqual(resp, return_value['flavor']['id'])

    def test_find_flavor_by_id(self):
        return_value = {"flavors": self.FLAVORS_LIST}
        mock_function = mock.Mock(return_value=return_value)
        self.useFixture(MonkeyPatch(self.CLIENT_MOCK + '.list_flavors',
                                    mock_function))
        resp = self.Service.find_flavor_by_id("MyFakeID")
        self.assertEqual(resp, "MyFakeID")
        # test no flavor found case
        resp = self.Service.find_flavor_by_id("NotExist")
        self.assertEqual(resp, None)

    def test_find_flavor_by_name(self):
        return_value = {"flavors": self.FLAVORS_LIST}
        mock_function = mock.Mock(return_value=return_value)
        self.useFixture(MonkeyPatch(self.CLIENT_MOCK + '.list_flavors',
                                    mock_function))
        resp = self.Service.find_flavor_by_name("MyID")
        self.assertEqual(resp, "MyFakeID")
        # test no flavor found case
        resp = self.Service.find_flavor_by_name("NotExist")
        self.assertEqual(resp, None)
