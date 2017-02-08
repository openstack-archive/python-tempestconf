# -*- coding: utf-8 -*-

# Copyright 2017 Red Hat, Inc.
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


from config_tempest import config_tempest as tool
from config_tempest.tests import base
from fixtures import MonkeyPatch
import logging
from mock import Mock

# disable logging when running unit tests
logging.disable(logging.CRITICAL)


def _get_conf(V2, V3):
    """Creates fake conf for testing purposes"""
    conf = tool.TempestConf()
    uri = "http://172.16.52.151:5000/"
    conf.set("identity", "username", "demo")
    conf.set("identity", "password", "secret")
    conf.set("identity", "tenant_name", "demo")
    conf.set("identity", "disable_ssl_certificate_validation", "true")
    conf.set("identity", "auth_version", "v3")
    conf.set("identity", "uri", uri + V2, priority=True)
    conf.set("identity", "uri_v3", uri + V3)
    conf.set("identity", "admin_username", "admin")
    conf.set("identity", "admin_tenant_name", "adminTenant")
    conf.set("identity", "admin_password", "adminPass")
    conf.set("auth", "allow_tenant_isolation", "False")
    return conf


def _get_clients(conf, admin=False):
    """Returns ClientManager instance"""
    return tool.ClientManager(conf, admin=admin)


class TestClientManager(base.TestCase):

    def setUp(self):
        super(TestClientManager, self).setUp()
        self.conf = _get_conf("v2.0", "v3")
        self.client = _get_clients(self.conf)

    def test_get_credentials_v2(self):
        mock = Mock()
        function2mock = 'config_tempest.config_tempest.auth.get_credentials'
        self.useFixture(MonkeyPatch(function2mock, mock))
        self.client.get_credentials(self.conf, "name", "Tname", "pass")
        mock.assert_called_with(auth_url=None,
                                fill_in=False,
                                identity_version='v2',
                                disable_ssl_certificate_validation='true',
                                ca_certs=None,
                                password='pass',
                                tenant_name='Tname',
                                username='name')

    def test_get_credentials_v3(self):
        mock = Mock()
        function2mock = 'config_tempest.config_tempest.auth.get_credentials'
        self.useFixture(MonkeyPatch(function2mock, mock))
        self.client.get_credentials(self.conf, "name", "project_name",
                                    "pass", identity_version='v3')
        mock.assert_called_with(auth_url=None,
                                fill_in=False,
                                identity_version='v3',
                                disable_ssl_certificate_validation='true',
                                ca_certs=None,
                                password='pass',
                                username='name',
                                project_name='project_name',
                                domain_name='Default',
                                user_domain_name='Default')

    def test_get_auth_provider_keystone_v2(self):
        # check if method returns correct method - KeystoneV2AuthProvider
        mock = Mock()
        # mock V2Provider, if other provider is called, it fails
        func2mock = 'config_tempest.config_tempest.auth.KeystoneV2AuthProvider'
        self.useFixture(MonkeyPatch(func2mock, mock))
        resp = self.client.get_auth_provider(self.conf, "")
        self.assertEqual(resp, mock())
        # check parameters of returned function
        self.client.get_auth_provider(self.conf, "")
        mock.assert_called_with('', 'http://172.16.52.151:5000/v2.0',
                                'true', None)

    def test_get_auth_provider_keystone_v3(self):
        # check if method returns KeystoneV3AuthProvider
        # make isinstance return True
        mockIsInstance = Mock(return_value=True)
        self.useFixture(MonkeyPatch('config_tempest.config_tempest.isinstance',
                                    mockIsInstance))
        mock = Mock()
        # mock V3Provider, if other provider is called, it fails
        func2mock = 'config_tempest.config_tempest.auth.KeystoneV3AuthProvider'
        self.useFixture(MonkeyPatch(func2mock, mock))
        resp = self.client.get_auth_provider(self.conf, "")
        self.assertEqual(resp, mock())
        # check parameters of returned function
        self.client.get_auth_provider(self.conf, "")
        mock.assert_called_with('', 'http://172.16.52.151:5000/v3',
                                'true', None)

    def test_get_identity_version_v2(self):
        resp = self.client.get_identity_version(self.conf)
        self.assertEqual(resp, 'v2')

    def test_get_identity_version_v3(self):
        conf = _get_conf("v3", "v3")  # uri has to be v3
        resp = self.client.get_identity_version(conf)
        self.assertEqual(resp, 'v3')

    def test_init_manager_as_admin(self):
        mock = Mock(return_value={"id": "my_fake_id"})
        func2mock = 'config_tempest.config_tempest.identity.get_tenant_by_name'
        self.useFixture(MonkeyPatch(func2mock, mock))
        tool.ClientManager(self.conf, admin=True)
        # check if admin credentials were set
        admin_tenant = self.conf.get("identity", "admin_tenant_name")
        admin_password = self.conf.get("identity", "admin_password")
        self.assertEqual(self.conf.get("identity", "admin_username"), "admin")
        self.assertEqual(admin_tenant, "adminTenant")
        self.assertEqual(admin_password, "adminPass")
        # check if admin tenant id was set
        admin_tenant_id = self.conf.get("identity", "admin_tenant_id")
        self.assertEqual(admin_tenant_id, "my_fake_id")


class TestTempestConf(base.TestCase):
    def setUp(self):
        super(TestTempestConf, self).setUp()
        self.conf = tool.TempestConf()

    def test_set_value(self):
        resp = self.conf.set("section", "key", "value")
        self.assertTrue(resp)
        self.assertEqual(self.conf.get("section", "key"), "value")
        self.assertEqual(self.conf.get_defaulted("section", "key"), "value")

    def test_set_value_overwrite(self):
        # set value wihout priority (default: priority=False)
        resp = self.conf.set("section", "key", "value")
        # value should be overwritten, because it wasn't set with priority
        resp = self.conf.set("section", "key", "value")
        self.assertTrue(resp)

    def test_set_value_overwrite_priority(self):
        resp = self.conf.set("sectionPriority", "key", "value", priority=True)
        resp = self.conf.set("sectionPriority", "key", "value")
        self.assertFalse(resp)

    def test_set_value_overwrite_by_priority(self):
        resp = self.conf.set("section", "key", "value")
        resp = self.conf.set("section", "key", "value", priority=True)
        self.assertTrue(resp)

    def test_set_value_overwrite_priority_by_priority(self):
        resp = self.conf.set("sectionPriority", "key", "value", priority=True)
        resp = self.conf.set("sectionPriority", "key", "value", priority=True)
        self.assertTrue(resp)

    def test_get_bool_value(self):
        self.assertTrue(self.conf.get_bool_value("True"))
        self.assertFalse(self.conf.get_bool_value("False"))
        self.assertRaises(ValueError, self.conf.get_bool_value, "no")


class TestConfigTempest(base.TestCase):

    FAKE_SERVICES = {
        'compute': {
            'url': 'http://172.16.52.151:8774/v2.1/402486',
            'extensions': ['NMN', 'OS-DCF', 'OS-EXT-AZ', 'OS-EXT-IMG-SIZE'],
            'versions': ['v2.0', 'v2.1']
        }, 'network': {
            'url': 'http://172.16.52.151:9696',
            'extensions': ['default-subnetpools', 'network-ip-availability'],
            'versions': ['v2.0']
        }, 'image': {
            'url': 'http://172.16.52.151:9292',
            'extensions': [],
            'versions': ['v2.4', 'v2.3', 'v2.2']
        }, 'volume': {
            'url': 'http://172.16.52.151:8776/v1/402486',
            'extensions': ['OS-SCH-HNT', 'os-hosts'],
            'versions': ['v1.0', 'v2.0', 'v3.0']
        }, 'identity': {
            'url': 'http://172.16.52.151:5000/v3',
            'versions': ['v3.8', 'v2.0']
        }, 'ec2': {
            'url': 'http://172.16.52.151:5000'
        }, 's3': {
            'url': 'http://172.16.52.151:5000'
        }
    }

    def setUp(self):
        super(TestConfigTempest, self).setUp()
        self.conf = _get_conf("v2.0", "v3")

    def test_configure_boto(self):
        tool.configure_boto(self.conf, self.FAKE_SERVICES)
        expected_url = "http://172.16.52.151:5000"
        self.assertEqual(self.conf.get("boto", "ec2_url"), expected_url)
        self.assertEqual(self.conf.get("boto", "s3_url"), expected_url)

    def test_configure_horizon(self):
        mock = Mock(return_value=True)
        self.useFixture(MonkeyPatch('urllib2.urlopen', mock))
        tool.configure_horizon(self.conf)
        self.assertEqual(self.conf.get('service_available', 'horizon'), "True")
        self.assertEqual(self.conf.get('dashboard', 'dashboard_url'),
                         "http://172.16.52.151/dashboard/")
        self.assertEqual(self.conf.get('dashboard', 'login_url'),
                         "http://172.16.52.151/dashboard/auth/login/")


class TestFindOrCreateFlavor(base.TestCase):

    CLIENT_MOCK = 'tempest.lib.services.compute.flavors_client.FlavorsClient'
    FLAVORS_LIST = [
        {"id": "Fakeid", "name": "Name"},
        {"id": "MyFakeID", "name": "MyID"}
    ]

    def setUp(self):
        super(TestFindOrCreateFlavor, self).setUp()
        conf = _get_conf("v2.0", "v3")
        self.client = _get_clients(conf).flavors

    def _mock_function(self, return_value, func2mock, flavor_name,
                       expected_resp, allow_creation=False, flavor_id=None):
        mock = Mock(return_value=return_value)
        self.useFixture(MonkeyPatch(self.CLIENT_MOCK + func2mock, mock))
        resp = tool.find_or_create_flavor(self.client,
                                          flavor_id=flavor_id,
                                          flavor_name=flavor_name,
                                          allow_creation=allow_creation)
        self.assertEqual(resp, expected_resp)

    def test_create_flavor_not_allowed(self):
        exc = Exception
        self.assertRaises(exc,
                          tool.find_or_create_flavor,
                          client=self.client,
                          flavor_id="id",
                          flavor_name="name",
                          allow_creation=False)

    def test_create_flavor(self):
        return_value = {"flavor": {"id": "MyFakeID", "name": "MyID"}}
        # mock list_flavors() to return empty list
        mock = Mock(return_value={"flavors": []})
        self.useFixture(MonkeyPatch(self.CLIENT_MOCK + '.list_flavors', mock))
        self._mock_function(return_value=return_value,
                            func2mock='.create_flavor',
                            flavor_name="MyID",
                            expected_resp="MyFakeID",
                            allow_creation=True)

    def test_find_flavor_by_id(self):
        self._mock_function(return_value={"flavors": self.FLAVORS_LIST},
                            func2mock='.list_flavors',
                            flavor_id="MyFakeID",
                            flavor_name=None,
                            expected_resp="MyFakeID")

    def test_find_flavor_by_name(self):
        self._mock_function(return_value={"flavors": self.FLAVORS_LIST},
                            func2mock='.list_flavors',
                            flavor_name="MyID",
                            expected_resp="MyFakeID")


class TestFindImage(base.TestCase):

    CLIENT_MOCK = 'tempest.lib.services.image.v2.images_client.ImagesClient'
    IMAGES_LIST = [
        {"status": "active", "name": "ImageName"},
        {"status": "default", "name": "MyImage"},
        {"status": "active", "name": "MyImage"}
    ]

    def setUp(self):
        super(TestFindImage, self).setUp()
        conf = _get_conf("v2.0", "v3")
        self.client = _get_clients(conf).images

    def _mock_list_images(self, return_value, image_name, expected_resp):
        mock = Mock(return_value=return_value)
        func2mock = self.CLIENT_MOCK + '.list_images'
        self.useFixture(MonkeyPatch(func2mock, mock))
        resp = tool._find_image(client=self.client,
                                image_id=None,
                                image_name=image_name)
        self.assertEqual(resp, expected_resp)

    def test_find_image_found(self):
        expected_resp = {"status": "default", "name": "MyImage"}
        self._mock_list_images(return_value={"images": self.IMAGES_LIST},
                               image_name="MyImage",
                               expected_resp=expected_resp)

    def test_find_image_not_found(self):
        self._mock_list_images(return_value={"images": self.IMAGES_LIST},
                               image_name="DoesNotExist",
                               expected_resp=None)
