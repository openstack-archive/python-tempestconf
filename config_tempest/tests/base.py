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

from config_tempest import api_discovery as api
from config_tempest import config_tempest as tool
from fixtures import MonkeyPatch
import json
import mock
from oslotest import base


class BaseConfigTempestTest(base.BaseTestCase):

    """Test case base class for all config_tempest unit tests"""

    def _get_conf(self, V2, V3):
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
        conf.set("auth", "use_dynamic_credentials", "False")
        return conf

    def _get_alt_conf(self, V2, V3):
        """Contains newer params in place of the deprecated params"""
        conf = tool.TempestConf()
        uri = "http://172.16.52.151:5000/"
        conf.set("identity", "username", "demo")
        conf.set("identity", "password", "secret")
        conf.set("identity", "tenant_name", "demo")
        conf.set("identity", "disable_ssl_certificate_validation", "true")
        conf.set("identity", "auth_version", "v3")
        conf.set("identity", "uri", uri + V2, priority=True)
        conf.set("identity", "uri_v3", uri + V3)
        conf.set("auth", "admin_username", "admin")
        conf.set("auth", "admin_project_name", "adminTenant")
        conf.set("auth", "admin_password", "adminPass")
        conf.set("auth", "use_dynamic_credentials", "True")
        return conf

    @mock.patch('os_client_config.cloud_config.CloudConfig')
    def _get_clients(self, conf, mock_args, admin=False):
        """Returns ClientManager instance"""
        mock_function = mock.Mock(return_value=False)
        func2mock = 'os_client_config.cloud_config.CloudConfig.config.get'
        self.useFixture(MonkeyPatch(func2mock, mock_function))
        return tool.ClientManager(conf, admin=admin)


class BaseServiceTest(base.BaseTestCase):

    """Test case base class for all api_discovery unit tests"""

    FAKE_TOKEN = "s6d5f45sdf4s564f4s6464sdfsd514"
    FAKE_HEADERS = {
        'Accept': 'application/json', 'X-Auth-Token': FAKE_TOKEN
    }
    FAKE_URL = "http://10.200.16.10:8774/"
    FAKE_VERSIONS = (
        {
            "versions": [{
                "status": "SUPPORTED",
                "updated": "2011-01-21T11:33:21Z",
                "links": [{
                    "href": "http://10.200.16.10:8774/v2 / ",
                    "rel": "self "
                }],
                "min_version": "",
                "version": "",
                "id": "v2.0",
                "values": [
                    {"id": 'v3.8'}
                ]
            }, {
                "status": "CURRENT",
                "updated": "2013-07-23T11:33:21Z",
                "links": [{
                    "href": "http://10.200.16.10:8774/v2.1/",
                    "rel": "self"
                }],
                "min_version": "2.1",
                "version": "2.41",
                "id": "v2.1",
                "values": [
                    {"id": 'v2.0'}
                ]
            }]
        }
    )
    FAKE_IDENTITY_VERSIONS = (
        {
            'versions': {
                'values': [{
                    'status': 'stable',
                    'id': 'v3.8',
                }, {
                    'status': 'deprecated',
                    'id': 'v2.0',
                }]
            }
        }
    )
    FAKE_EXTENSIONS = (
        {
            "extensions": [{
                "updated": "2014-12-03T00:00:00Z",
                "name": "Multinic",
                "namespace": "http://docs.openstack.org/compute/ext/fake_xml",
                "alias": "NMN",
                "description": "Multiple network support."
            }, {
                "updated": "2014-12-03T00:00:00Z",
                "name": "DiskConfig",
                "namespace": "http://docs.openstack.org/compute/ext/fake_xml",
                "alias": "OS-DCF",
                "description": "Disk Management Extension."
            }]
        }
    )
    FAKE_IDENTITY_EXTENSIONS = (
        {
            "extensions": {
                'values': [{
                    'alias': 'OS-DCF',
                    'id': 'v3.8',
                }, {
                    'alias': 'NMN',
                    'id': 'v2.0',
                }]
            }
        }
    )
    FAKE_STORAGE_EXTENSIONS = (
        {
            "formpost": {},
            "methods": ["GET", "HEAD", "PUT", "POST", "DELETE"],
            "ratelimit": {
                "account_ratelimit": 0.0,
                "max_sleep_time_seconds": 60.0,
                "container_ratelimits": []
            },
            "account_quotas": {},
            "swift": {
                "container_listing_limit": 10000,
                "allow_account_management": True,
                "max_container_name_length": 256
            }
        }
    )

    class FakeRequestResponse(object):
        URL = 'http://docs.openstack.org/api/openstack-identity/3/ext/'
        FAKE_V3_EXTENSIONS = (
            {
                'resources': {
                    URL + 'OS-INHERIT/1.0/rel/domain_user_'
                        + 'role_inherited_to_projects': "",

                    URL + 'OS-SIMPLE-CERT/1.0/rel/ca_certificate': "",

                    URL + 'OS-EP-FILTER/1.0/rel/endpoint_group_to_'
                        + 'project_association': "",

                    URL + 'OS-EP-FILTER/1.0/rel/project_endpoint': "",

                    URL + 'OS-OAUTH1/1.0/rel/user_access_token_roles': ""
                }
            }
        )

        def __init__(self):
            self.content = json.dumps(self.FAKE_V3_EXTENSIONS)

    def _fake_service_do_get_method(self, fake_data):
        function2mock = 'config_tempest.api_discovery.Service.do_get'
        do_get_output = json.dumps(fake_data)
        mocked_do_get = mock.Mock()
        mocked_do_get.return_value = do_get_output
        self.useFixture(MonkeyPatch(function2mock, mocked_do_get))

    def _test_get_service_class(self, service, cls):
        resp = api.get_service_class(service)
        self.assertEqual(resp, cls)

    def _get_extensions(self, service, expected_resp, fake_data):
        self._fake_service_do_get_method(fake_data)
        resp = service.get_extensions()
        self.assertItemsEqual(resp, expected_resp)

    def _test_deserialize_versions(self, service, expected_resp, fake_data):
        resp = service.deserialize_versions(fake_data)
        self.assertItemsEqual(resp, expected_resp)
