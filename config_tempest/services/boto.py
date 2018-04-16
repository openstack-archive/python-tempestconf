# Copyright 2016 Red Hat, Inc.
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


def configure_boto(conf, ec2_service=None, s3_service=None):
    """Set boto URLs based on discovered APIs.

    :type ec2_service: config_tempest.services.base.Service
    :type s3_service: config_tempest.services.base.Service
    """
    if ec2_service:
        conf.set('boto', 'ec2_url', ec2_service.service_url)
    if s3_service:
        conf.set('boto', 's3_url', s3_service.service_url)
