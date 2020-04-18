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

from config_tempest import profile
from config_tempest.tests.base import BaseConfigTempestTest


class TestProfile(BaseConfigTempestTest):

    def test_convert_remove_append(self):
        in_data = {
            'section.key1': 'value1',
            'section.key2': 'value1,value2'
        }
        expected = [
            'section.key1=value1',
            'section.key2=value1,value2'
        ]
        out_data = profile._convert_remove_append(in_data)
        self.assertItemsEqual(expected, out_data)

    @mock.patch('config_tempest.profile._read_yaml_file')
    def test_read_profile_file(self, mock_read_yaml):
        profile_data = {
            'create': True,
            'overrides': {
                'auth.use_dynamic_credentials': True
            },
            'append': {
                'network-feature-enabled.api_extensions': 'ext',
                'identity-feature-enabled.api_extensions': ['ext1', 'ext2'],
                'compute-feature-enabled.api_extensions': 'ext3,ext4'
            },
            'remove': {
                'network-feature-enabled.api_extensions': 'dvr',
                'identity-feature-enabled.api_extensions': ['dvr1', 'dvr2'],
                'compute-feature-enabled.api_extensions': 'dvr3,dvr4'
            },
            'network-id': 'network_id',
            'out': './etc/tempest.conf'
        }
        mock_read_yaml.return_value = profile_data
        ret_dict = profile.read_profile_file('path')
        expected = {
            'create': True,
            'remove': [
                'network-feature-enabled.api_extensions=dvr',
                'identity-feature-enabled.api_extensions=dvr1,dvr2',
                'compute-feature-enabled.api_extensions=dvr3,dvr4'
            ],
            'network-id': 'network_id',
            'overrides': [('auth', 'use_dynamic_credentials', 'True')],
            'append': [
                'network-feature-enabled.api_extensions=ext',
                'identity-feature-enabled.api_extensions=ext1,ext2',
                'compute-feature-enabled.api_extensions=ext3,ext4'
            ],
            'out': './etc/tempest.conf'
        }
        for key in ['create', 'network-id', 'out']:
            self.assertEqual(expected[key], ret_dict[key])
        for key in ['remove', 'overrides', 'append']:
            self.assertListEqual(sorted(expected[key]), sorted(ret_dict[key]))
