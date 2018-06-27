# -*- coding: utf-8 -*-

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

import mock

from config_tempest import tempest_conf
from config_tempest.tests.base import BaseConfigTempestTest


class TestTempestConf(BaseConfigTempestTest):
    def setUp(self):
        super(TestTempestConf, self).setUp()
        self.conf = tempest_conf.TempestConf()

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

    def test_remove_values(self):
        api_exts = "router_availability_zone,rbac-policies,pagination,sorting,"
        api_exts += "standard-attr-description,router,binding,metering,"
        api_exts += "allowed-address-pairs,project-id,dvr,l3-flavors,tag-ext"
        remove_exts = ["router", "project-id", "dvr"]
        remove = {
            "identity.username": ["demo"],
            "identity.project_name": ["project"],
            "compute.image_ssh_user": ["rhel", "cirros"],
            "network-feature-enabled.api_extensions": remove_exts
        }
        self.conf = self._get_conf("v2.0", "v3")
        self.conf.set("compute", "image_ssh_user", "cirros")
        self.conf.set("network-feature-enabled", "api_extensions", api_exts)
        self.conf.remove_values(remove)
        self.assertFalse(self.conf.has_option("identity", "username"))
        self.assertTrue(self.conf.has_option("identity", "project_name"))
        self.assertFalse(self.conf.has_option("compute", "image_ssh_user"))
        conf_exts = self.conf.get("network-feature-enabled", "api_extensions")
        conf_exts = conf_exts.split(',')
        for ext in api_exts.split(','):
            if ext in remove_exts:
                self.assertFalse(ext in conf_exts)
            else:
                self.assertTrue(ext in conf_exts)

    def test_remove_values_having_hyphen(self):
        api_exts = "dvr, l3-flavors, rbac-policies, project-id"
        remove_exts = ["dvr", "project-id"]
        remove = {
            "network-feature-enabled.api-extensions": remove_exts
        }
        self.conf = self._get_conf("v2.0", "v3")
        self.conf.set("network-feature-enabled", "api-extensions", api_exts)
        self.conf.remove_values(remove)
        conf_exts = self.conf.get("network-feature-enabled", "api-extensions")
        conf_exts = conf_exts.split(',')
        for ext in api_exts.split(','):
            if ext in remove_exts:
                self.assertFalse(ext in conf_exts)
            else:
                self.assertTrue(ext in conf_exts)

    @mock.patch('config_tempest.tempest_conf.C.LOG')
    def test_remove_not_defined_values(self, mock_logging):
        self.conf.remove_values({"notExistSection.key": []})
        # check if LOG.error was called
        self.assertTrue(mock_logging.error.called)
        self.conf.remove_values({"section.notExistKey": []})
        # check if LOG.error was called
        self.assertTrue(mock_logging.error.called)
