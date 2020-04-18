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

from unittest import mock

from config_tempest import tempest_conf
from config_tempest.tests.base import BaseConfigTempestTest


class TestTempestConf(BaseConfigTempestTest):
    def setUp(self):
        super(TestTempestConf, self).setUp()
        self.conf = tempest_conf.TempestConf()

    def test_set_value(self):
        conf = self._get_conf("v2.0", "v3")
        resp = conf.set("section", "key", "value")
        self.assertTrue(resp)
        self.assertEqual(conf.get("section", "key"), "value")
        self.assertEqual(conf.get_defaulted("section", "key"), "value")

    def test_set_value_overwrite(self):
        conf = self._get_conf("v2.0", "v3")
        # set value without priority (default: priority=False)
        resp = conf.set("section", "key", "value")
        self.assertTrue(resp)
        self.assertEqual(conf.get("section", "key"), "value")
        # value should be overwritten, because it wasn't set with priority
        resp = conf.set("section", "key", "new_value")
        self.assertTrue(resp)
        self.assertEqual(conf.get("section", "key"), "new_value")

    def test_set_value_overwrite_priority(self):
        conf = self._get_conf("v2.0", "v3")
        resp = conf.set("sectionPriority", "key", "value", priority=True)
        resp = conf.set("sectionPriority", "key", "new_value")
        self.assertFalse(resp)
        self.assertEqual(conf.get("sectionPriority", "key"), "value")

    def test_set_value_overwrite_by_priority(self):
        conf = self._get_conf("v2.0", "v3")
        resp = conf.set("section", "key", "value")
        self.assertTrue(resp)
        self.assertEqual(conf.get("section", "key"), "value")
        resp = conf.set("section", "key", "new_value", priority=True)
        self.assertTrue(resp)
        self.assertEqual(conf.get("section", "key"), "new_value")

    def test_set_value_overwrite_priority_by_priority(self):
        conf = self._get_conf("v2.0", "v3")
        resp = conf.set("sectionPriority", "key", "value", priority=True)
        self.assertTrue(resp)
        self.assertEqual(conf.get("sectionPriority", "key"), "value")
        resp = conf.set("sectionPriority", "key", "new_value", priority=True)
        self.assertTrue(resp)
        self.assertEqual(conf.get("sectionPriority", "key"), "new_value")

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
        conf = self._get_conf("v2.0", "v3")
        conf.set("compute", "image_ssh_user", "cirros")
        conf.set("network-feature-enabled", "api_extensions", api_exts)
        conf.remove_values(remove)
        self.assertFalse(conf.has_option("identity", "username"))
        self.assertTrue(conf.has_option("identity", "project_name"))
        self.assertFalse(conf.has_option("compute", "image_ssh_user"))
        conf_exts = conf.get("network-feature-enabled", "api_extensions")
        conf_exts = conf_exts.split(',')
        for ext in api_exts.split(','):
            if ext in remove_exts:
                self.assertFalse(ext in conf_exts)
            else:
                self.assertTrue(ext in conf_exts)

    def test_remove_values_having_hyphen(self):
        api_exts = "dvr,l3-flavors,rbac-policies,project-id"
        remove_exts = ["dvr", "project-id"]
        remove = {
            "network-feature-enabled.api_extensions": remove_exts
        }
        conf = self._get_conf("v2.0", "v3")
        conf.set("network-feature-enabled", "api_extensions", api_exts)
        conf.remove_values(remove)
        conf_exts = conf.get("network-feature-enabled", "api_extensions")
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

    def test_append_values(self):
        api_exts = "dvr,l3-flavors,rbac-policies"
        add_exts = ["dvr", "project-id"]
        add = {
            "compute-feature-enabled.api_extensions": add_exts
        }
        self.conf = self._get_conf("v2.0", "v3")
        self.conf.set("compute-feature-enabled", "api_extensions", api_exts)
        self.conf.append_values(add)
        conf_exts = self.conf.get("compute-feature-enabled", "api_extensions")
        conf_exts = conf_exts.split(',')
        self.assertEqual(len(conf_exts), 4)
        self.assertTrue("project-id" in conf_exts)

    def test_append_values_with_overrides(self):
        # Test if --add option can override an option which was
        # passed to python-tempestconf as an override, it shouldn't
        api_exts = "dvr,l3-flavors,rbac-policies"
        add_exts = ["dvr", "project-id"]
        add = {
            "compute-feature-enabled.api_extensions": add_exts
        }
        self.conf = self._get_conf("v2.0", "v3")
        # let's simulate a situation when the following apis were set
        # via overrides => they are set with the priority
        self.conf.set("compute-feature-enabled", "api_extensions",
                      api_exts, priority=True)
        self.conf.append_values(add)
        conf_exts = self.conf.get("compute-feature-enabled", "api_extensions")
        conf_exts = conf_exts.split(',')
        # if there are still 3 extensions, no new was added
        self.assertEqual(len(conf_exts), 3)
        # option added via --add shouldn't be there
        self.assertFalse("project-id" in conf_exts)
        self.assertTrue("dvr" in conf_exts)
        self.assertTrue("l3-flavors" in conf_exts)
        self.assertTrue("rbac-policies" in conf_exts)
