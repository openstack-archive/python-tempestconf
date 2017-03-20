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


class BaseConfigTempestTest(base.TestCase):

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
        conf.set("auth", "allow_tenant_isolation", "False")
        return conf

    def _get_clients(self, conf, admin=False):
        """Returns ClientManager instance"""
        return tool.ClientManager(conf, admin=admin)
