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

import ConfigParser

from config_tempest.services import base
from config_tempest.services import boto
from config_tempest.tempest_conf import TempestConf
from config_tempest.tests.base import BaseServiceTest


class TestBotoService(BaseServiceTest):
    def setUp(self):
        super(TestBotoService, self).setUp()
        self.conf = TempestConf()
        self.es2 = base.Service("ec2",
                                self.FAKE_URL,
                                self.FAKE_TOKEN,
                                disable_ssl_validation=False)
        self.s3 = base.Service("s3",
                               self.FAKE_URL,
                               self.FAKE_TOKEN,
                               disable_ssl_validation=False)

    def test_configure_boto(self):
        boto.configure_boto(self.conf)
        self._assert_conf_get_not_raises(ConfigParser.NoSectionError,
                                         "boto",
                                         "ec2_url")
        self._assert_conf_get_not_raises(ConfigParser.NoSectionError,
                                         "boto",
                                         "s3_url")
        boto.configure_boto(self.conf, self.es2, self.s3)
        self.assertEqual(self.conf.get("boto", "ec2_url"), self.FAKE_URL)
        self.assertEqual(self.conf.get("boto", "s3_url"), self.FAKE_URL)
