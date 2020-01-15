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
import json
import logging
import mock
from oslotest import base

from config_tempest.clients import ClientManager
from config_tempest.credentials import Credentials
from config_tempest import tempest_conf

# disable logging when running unit tests
logging.disable(logging.CRITICAL)


class BaseConfigTempestTest(base.BaseTestCase):

    """Test case base class for all config_tempest unit tests"""

    FAKE_V3_VERSIONS = (
        [{
            'status': 'stable',
            'id': 'v3.8',
        }, {
            'status': 'deprecated',
            'id': 'v2.0',
        }]
    )
    FAKE_V2_VERSIONS = (
        [{
            'status': 'deprecated',
            'id': 'v3.8',
        }, {
            'status': 'stable',
            'id': 'v2.0',
        }]
    )

    def _get_conf(self, V2, V3):
        """Creates fake conf for testing purposes"""
        conf = tempest_conf.TempestConf()
        uri = "http://172.16.52.151:5000/"
        conf.set("identity", "username", "demo")
        conf.set("identity", "password", "secret")
        conf.set("identity", "project_name", "demo")
        conf.set("identity", "disable_ssl_certificate_validation", "true")
        conf.set("identity", "auth_version", "v3")
        conf.set("identity", "uri", uri + V2, priority=True)
        conf.set("identity", "uri_v3", uri + V3)
        conf.set("auth", "admin_username", "admin")
        conf.set("auth", "admin_project_name", "adminProject")
        conf.set("auth", "admin_password", "adminPass")
        conf.set("auth", "use_dynamic_credentials", "False", priority=True)
        return conf

    def _get_alt_conf(self, V2, V3):
        """Contains newer params in place of the deprecated params"""
        conf = tempest_conf.TempestConf()
        uri = "http://172.16.52.151:5000/"
        conf.set("identity", "username", "demo")
        conf.set("identity", "password", "secret")
        conf.set("identity", "project_name", "demo")
        conf.set("identity", "disable_ssl_certificate_validation", "true")
        conf.set("identity", "auth_version", "v3")
        conf.set("identity", "uri", uri + V2, priority=True)
        conf.set("identity", "uri_v3", uri + V3)
        conf.set("auth", "admin_username", "admin")
        conf.set("auth", "admin_project_name", "adminProject")
        conf.set("auth", "admin_password", "adminPass")
        conf.set("auth", "use_dynamic_credentials", "True", priority=True)
        return conf

    def _get_creds(self, conf, admin=False, v2=False):
        # We return creds configured to v2 or v3
        func2mock = 'config_tempest.credentials.Credentials._list_versions'
        return_value = self.FAKE_V3_VERSIONS
        if v2:
            return_value = self.FAKE_V2_VERSIONS
        mock_function = mock.Mock(return_value=return_value)
        self.useFixture(MonkeyPatch(func2mock, mock_function))
        return Credentials(conf, admin)

    def _get_clients(self, conf, creds=None):
        """Returns ClientManager instance"""
        if creds is None:
            creds = self._get_creds(conf, v2=True)
        return ClientManager(conf, creds)


class BaseServiceTest(base.BaseTestCase):

    """Test case base class for all api_discovery unit tests"""

    FAKE_TOKEN = "s6d5f45sdf4s564f4s6464sdfsd514"
    FAKE_CLIENT_MOCK = 'config_tempest.tests.base.BaseServiceTest' + \
                       '.FakeServiceClient'
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
            }, {
                "status": "DEPRECATED",
                "updated": "2013-07-23T11:33:21Z",
                "links": [{
                    "href": "http://10.200.16.10:8774/v1/",
                    "rel": "self"
                }],
                "min_version": "1.0",
                "version": "1.0",
                "id": "v1.0",
                "values": [
                    {"id": 'v1.0'}
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
    FAKE_IDENTITY_VERSION = (
        {
            'version': {
                'status': 'stable',
                'id': 'v3.8',
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
    FAKE_ROLES = (
        {
            "roles": [
                {
                    "name": "ResellerAdmin",
                    "id": "2b4df7a671a443d741c62b4df7a671a443d741c6",
                    "domain_id": None
                }
            ]
        }
    )
    FAKE_ACCOUNTS = (
        {
            'status': '200',
            u'content-length': '2',
            'content-location': 'http://192.168.122.120:8080/healthcheck',
            u'connection': 'close',
            u'x-trans-id': 'txec03483c96cd4958a5c6b-005b17c346',
            u'date': 'Wed, 06 Jun 2018 11:19:34 GMT',
            u'content-type': 'text/plain',
            u'x-openstack-request-id': 'txec03483c96cd4958a5c6b-005b17c346'
        },
        'OK')

    class FakeRequestResponse(object):
        URL = 'https://docs.openstack.org/api/openstack-identity/3/ext/'
        FAKE_V3_EXTENSIONS = (
            {
                'resources': {
                    URL + 'OS-INHERIT/1.0/rel/domain_user_' +
                          'role_inherited_to_projects': "",

                    URL + 'OS-SIMPLE-CERT/1.0/rel/ca_certificate': "",

                    URL + 'OS-EP-FILTER/1.0/rel/endpoint_group_to_' +
                          'project_association': "",

                    URL + 'OS-EP-FILTER/1.0/rel/project_endpoint': "",

                    URL + 'OS-OAUTH1/1.0/rel/user_access_token_roles': ""
                }
            }
        )

        def __init__(self, bytes_content=False):
            self.content = json.dumps(self.FAKE_V3_EXTENSIONS)
            if bytes_content:
                self.content = self.content.encode('utf-8')

    class FakeServiceClient(object):
        def __init__(self, services=None):
            self.client = mock.Mock()
            self.return_value = mock.Mock()
            self.services = services

        def list_networks(self):
            return self.return_value

        def list_services(self, **kwargs):
            return self.services

    def _fake_service_do_get_method(self, fake_data):
        function2mock = 'config_tempest.services.base.Service.do_get'
        do_get_output = json.dumps(fake_data)
        mocked_do_get = mock.Mock()
        mocked_do_get.return_value = do_get_output
        self.useFixture(MonkeyPatch(function2mock, mocked_do_get))

    def _set_get_extensions(self, service, expected_resp, fake_data):
        # mock do_get response
        self._fake_service_do_get_method(fake_data)
        # set the fake extensions
        service.set_extensions()
        # check if extensions were set
        self.assertItemsEqual(service.extensions, expected_resp)
        # check if get method returns the right data
        resp = service.get_extensions()
        self.assertItemsEqual(resp, expected_resp)

    def _set_get_versions(self, service, expected_resp, fake_data):
        # mock do_get response
        self._fake_service_do_get_method(fake_data)
        # set the fake versions
        service.set_versions()
        # check if versions were set
        self.assertItemsEqual(service.versions, expected_resp)
        # check if get method returns the right data
        resp = service.get_versions()
        self.assertItemsEqual(resp, expected_resp)

    def _test_deserialize_versions(self, service, expected_resp, fake_data):
        resp = service.deserialize_versions(fake_data)
        self.assertItemsEqual(resp, expected_resp)

    def _assert_conf_get_not_raises(self, exc, section, value):
        try:
            self.conf.get(section, value)
        except exc:
            return
        self.assertTrue(False)
