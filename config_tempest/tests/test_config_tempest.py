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

from fixtures import MonkeyPatch
import logging
import mock

from config_tempest.clients import ClientManager
from config_tempest import main as tool
from config_tempest import tempest_conf
from config_tempest.tests.base import BaseConfigTempestTest

# disable logging when running unit tests
logging.disable(logging.CRITICAL)


class TestOsClientConfigSupport(BaseConfigTempestTest):

    def setUp(self):
        super(TestOsClientConfigSupport, self).setUp()
        self.conf = self._get_conf("v2.0", "v3")

    def _check_credentials(self, manager, username, password, tenant_name):
        exp_user = manager.auth_provider.credentials._initial['username']
        exp_pass = manager.auth_provider.credentials._initial['password']
        exp_tenant = manager.auth_provider.credentials._initial['tenant_name']
        self.assertEqual(exp_user, username)
        self.assertEqual(exp_pass, password)
        self.assertEqual(exp_tenant, tenant_name)

    @mock.patch('os_client_config.cloud_config.CloudConfig')
    def _override_setup(self, mock_args):
        cloud_args = {
            'username': 'cloud_user',
            'password': 'cloud_pass',
            'project_name': 'cloud_project'
        }
        mock_function = mock.Mock(return_value=cloud_args)
        func2mock = 'os_client_config.cloud_config.CloudConfig.config.get'
        self.useFixture(MonkeyPatch(func2mock, mock_function))
        mock_function = mock.Mock(return_value={"id": "my_fake_id"})
        func2mock = ('config_tempest.clients.ProjectsClient.'
                     'get_project_by_name')
        self.useFixture(MonkeyPatch(func2mock, mock_function))

    def _obtain_client_config_data(self, non_admin):
        cloud_args = {
            'username': 'cloud_user',
            'password': 'cloud_pass',
            'project_name': 'cloud_project',
            'auth_url': 'http://auth.url.com/'
        }
        # create an empty conf
        conf = tempest_conf.TempestConf()
        conf.set('identity', 'uri', cloud_args['auth_url'], priority=True)
        # call the function and check if data were obtained properly
        tool.set_cloud_config_values(non_admin, cloud_args, conf)
        if non_admin:
            self.assertEqual(cloud_args['username'],
                             conf.get('identity', 'username'))
            self.assertEqual(cloud_args['password'],
                             conf.get('identity', 'password'))
            self.assertEqual(cloud_args['project_name'],
                             conf.get('identity', 'tenant_name'))
        else:
            self.assertEqual(cloud_args['username'],
                             conf.get('identity', 'admin_username'))
            self.assertEqual(cloud_args['password'],
                             conf.get('identity', 'admin_password'))
            self.assertEqual(cloud_args['project_name'],
                             conf.get('identity', 'admin_tenant_name'))

    def test_init_manager_client_config(self):
        self._obtain_client_config_data(True)

    def test_init_manager_client_config_as_admin(self):
        self._obtain_client_config_data(False)

    @mock.patch('os_client_config.cloud_config.CloudConfig')
    def test_init_manager_client_config_get_default(self, mock_args):
        mock_function = mock.Mock(return_value={})
        func2mock = 'os_client_config.cloud_config.CloudConfig.config.get'
        self.useFixture(MonkeyPatch(func2mock, mock_function))
        manager = ClientManager(self.conf, self._get_creds(self.conf))
        # cloud_args is empty => check if default credentials were used
        self._check_credentials(manager,
                                self.conf.get('identity', 'username'),
                                self.conf.get('identity', 'password'),
                                self.conf.get('identity', 'tenant_name'))

    def test_init_manager_client_config_override(self):
        self._override_setup()
        manager = ClientManager(self.conf, self._get_creds(self.conf))
        # check if cloud_args credentials were overrided by the ones set in CLI
        self._check_credentials(manager,
                                self.conf.get('identity', 'username'),
                                self.conf.get('identity', 'password'),
                                self.conf.get('identity', 'tenant_name'))

    def test_init_manager_client_config_admin_override(self):
        self._override_setup()
        creds = self._get_creds(self.conf, admin=True)
        manager = ClientManager(self.conf, creds)
        # check if cloud_args credentials were overrided by admin ones
        self._check_credentials(manager,
                                self.conf.get('identity', 'admin_username'),
                                self.conf.get('identity', 'admin_password'),
                                self.conf.get('identity', 'admin_tenant_name'))


class TestConfigTempest(BaseConfigTempestTest):

    FAKE_SERVICES = {
        'compute': {
            'url': 'http://172.16.52.151:8774/v2.1/402486',
            'extensions': ['NMN', 'OS-DCF', 'OS-EXT-AZ', 'OS-EXT-IMG-SIZE'],
            'versions': ['v2.0', 'v2.1']
        },
        'network': {
            'url': 'http://172.16.52.151:9696',
            'extensions': ['default-subnetpools', 'network-ip-availability'],
            'versions': ['v2.0']
        },
        'image': {
            'url': 'http://172.16.52.151:9292',
            'extensions': [],
            'versions': ['v2.4', 'v2.3', 'v2.2']
        },
        'volumev3': {
            'url': 'http://172.16.52.151:8776/v3/402486',
            'extensions': ['OS-SCH-HNT', 'os-hosts'],
            'versions': ['v2.0', 'v3.0']
        },
        'volume': {
            'url': 'http://172.16.52.151:8776/v1/402486',
            'extensions': [],
            'versions': []
        },
        'identity': {
            'url': 'http://172.16.52.151:5000/v3',
            'versions': ['v3.8', 'v2.0']
        },
        'ec2': {
            'url': 'http://172.16.52.151:5000'
        },
        's3': {
            'url': 'http://172.16.52.151:5000'
        }
    }

    def setUp(self):
        super(TestConfigTempest, self).setUp()
        self.conf = self._get_conf("v2.0", "v3")

    def _mock_get_identity_v3_extensions(self):
        mock_function = mock.Mock(return_value=['FAKE-EXTENSIONS'])
        func2mock = 'config_tempest.api_discovery.get_identity_v3_extensions'
        self.useFixture(MonkeyPatch(func2mock, mock_function))

    def test_check_volume_backup_service(self):
        client = self._get_clients(self.conf).volume_service
        CLIENT_MOCK = ('tempest.lib.services.volume.v2.'
                       'services_client.ServicesClient')
        func2mock = '.list_services'
        mock_function = mock.Mock(return_value={'services': []})
        self.useFixture(MonkeyPatch(CLIENT_MOCK + func2mock, mock_function))
        tool.check_volume_backup_service(client, self.conf, self.FAKE_SERVICES)
        self.assertEqual(self.conf.get('volume-feature-enabled', 'backup'),
                         'False')

    def test_check_ceilometer_service(self):
        client = self._get_clients(self.conf).service_client
        CLIENT_MOCK = ('tempest.lib.services.identity.v3.'
                       'services_client.ServicesClient')
        func2mock = '.list_services'
        mock_function = mock.Mock(return_value={'services': [
            {'name': 'ceilometer', 'enabled': True, 'type': 'metering'}]})

        self.useFixture(MonkeyPatch(CLIENT_MOCK + func2mock, mock_function))
        tool.check_ceilometer_service(client, self.conf, self.FAKE_SERVICES)
        self.assertEqual(self.conf.get('service_available', 'ceilometer'),
                         'True')

    def test_configure_keystone_feature_flags(self):
        tool.configure_keystone_feature_flags(self.conf, self.FAKE_SERVICES)
        self.assertEqual(
            self.conf.get('identity-feature-enabled',
                          'forbid_global_implied_dsr'), 'True')

    def test_configure_boto(self):
        tool.configure_boto(self.conf, self.FAKE_SERVICES)
        expected_url = "http://172.16.52.151:5000"
        self.assertEqual(self.conf.get("boto", "ec2_url"), expected_url)
        self.assertEqual(self.conf.get("boto", "s3_url"), expected_url)

    def test_configure_horizon_ipv4(self):
        mock_function = mock.Mock(return_value=True)
        self.useFixture(MonkeyPatch('urllib2.urlopen', mock_function))
        tool.configure_horizon(self.conf)
        self.assertEqual(self.conf.get('service_available', 'horizon'), "True")
        self.assertEqual(self.conf.get('dashboard', 'dashboard_url'),
                         "http://172.16.52.151/dashboard/")
        self.assertEqual(self.conf.get('dashboard', 'login_url'),
                         "http://172.16.52.151/dashboard/auth/login/")

    def test_configure_horizon_ipv6(self):
        mock_function = mock.Mock(return_value=True)
        self.useFixture(MonkeyPatch('urllib2.urlopen', mock_function))
        self.conf.set('identity', 'uri', 'http://[::1]:5000/v3', priority=True)
        tool.configure_horizon(self.conf)
        self.assertEqual(self.conf.get('service_available', 'horizon'), "True")
        self.assertEqual(self.conf.get('dashboard', 'dashboard_url'),
                         "http://[::1]/dashboard/")
        self.assertEqual(self.conf.get('dashboard', 'login_url'),
                         "http://[::1]/dashboard/auth/login/")

    def test_discovered_services(self):
        self._mock_get_identity_v3_extensions()
        tool.configure_discovered_services(self.conf, self.FAKE_SERVICES)
        # check enabled services
        enabled_services = ["image", "volume", "compute", "network"]
        # iterating through tuples = (service_name, codename)
        for service in tool.SERVICE_NAMES.iteritems():
            if service[0] in enabled_services:
                enabled = "True"
            else:
                enabled = "False"
            self.assertEqual(self.conf.get("service_available", service[1]),
                             enabled)

        # check versions
        for service, service_info in tool.SERVICE_VERSIONS.iteritems():
            section = service + '-feature-enabled'
            for version in service_info['supported_versions']:
                # only image v1 is expected to be False
                exp_support = str(not(service == "image" and version == "v1"))
                self.assertEqual(self.conf.get(section, 'api_' + version),
                                 exp_support)

        # check extensions
        for service, ext_key in tool.SERVICE_EXTENSION_KEY.iteritems():
            if service in self.FAKE_SERVICES:
                section = service + '-feature-enabled'
                if service == "identity":
                    exp_ext = ",FAKE-EXTENSIONS"
                else:
                    extensions = self.FAKE_SERVICES[service]['extensions']
                    exp_ext = ','.join(extensions)
                self.assertEqual(self.conf.get(section, 'api_extensions'),
                                 exp_ext)

    def test_discovered_services_volume_service_disabled(self):
        self.conf.set("services", "volume", "False")
        self._mock_get_identity_v3_extensions()
        tool.configure_discovered_services(self.conf, self.FAKE_SERVICES)
        self.assertFalse(self.conf.has_option("service_available", "cinder"))
        self.assertFalse(self.conf.has_option("volume-feature-enabled",
                                              "api_v1"))
        self.assertFalse(self.conf.has_option("volume-feature-enabled",
                                              "api_v2"))


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

    def _mock_create_tempest_flavor(self, mock_function):
        func2mock = 'config_tempest.main.find_or_create_flavor'
        self.useFixture(MonkeyPatch(func2mock, mock_function))
        tool.create_tempest_flavors(client=self.client,
                                    conf=self.conf,
                                    allow_creation=True)

    def _mock_find_or_create_flavor(self, return_value, func2mock, flavor_name,
                                    expected_resp, allow_creation=False,
                                    flavor_id=None):
        mock_function = mock.Mock(return_value=return_value)
        self.useFixture(MonkeyPatch(self.CLIENT_MOCK + func2mock,
                                    mock_function))
        resp = tool.find_or_create_flavor(self.client,
                                          flavor_id=flavor_id,
                                          flavor_name=flavor_name,
                                          allow_creation=allow_creation)
        self.assertEqual(resp, expected_resp)

    def test_create_tempest_flavors(self):
        mock_function = mock.Mock(return_value="FakeID")
        self._mock_create_tempest_flavor(mock_function)
        self.assertEqual(self.conf.get('compute', 'flavor_ref'), "FakeID")
        self.assertEqual(self.conf.get('compute', 'flavor_ref_alt'), "FakeID")
        calls = [mock.call(self.client, None, 'm1.nano', True, ram=64),
                 mock.call(self.client, None, 'm1.micro', True, ram=128)]
        mock_function.assert_has_calls(calls, any_order=True)

    def test_create_tempest_flavors_overwrite(self):
        mock_function = mock.Mock(return_value="FakeID")
        self.conf.set('compute', 'flavor_ref', "FAKE_ID")
        self.conf.set('compute', 'flavor_ref_alt', "FAKE_ID")
        self._mock_create_tempest_flavor(mock_function)
        calls = [mock.call(self.client, "FAKE_ID", 'm1.nano', True, ram=64),
                 mock.call(self.client, "FAKE_ID", 'm1.micro', True, ram=128)]
        mock_function.assert_has_calls(calls, any_order=True)

    def test_create_flavor_not_allowed(self):
        # mock list_flavors() to return empty list
        mock_function = mock.Mock(return_value={"flavors": []})
        self.useFixture(MonkeyPatch(self.CLIENT_MOCK + '.list_flavors',
                                    mock_function))
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
