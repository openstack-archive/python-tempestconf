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
