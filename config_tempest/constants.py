# Copyright 2013, 2016, 2018 Red Hat, Inc.
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

import logging
import os

LOG = logging.getLogger(__name__)

# Get the current tempest workspace path
TEMPEST_WORKSPACE = os.getcwd()

DEPLOYER_INPUT = os.path.join(os.path.expanduser("~"),
                              "tempest-deployer-input.conf")
DEFAULT_IMAGE = ("https://download.cirros-cloud.net/0.4.0/"
                 "cirros-0.4.0-x86_64-disk.img")
DEFAULT_IMAGE_FORMAT = 'qcow2'

DEFAULT_FLAVOR_RAM = 64
DEFAULT_FLAVOR_RAM_ALT = 128
DEFAULT_FLAVOR_DISK = 1
DEFAULT_FLAVOR_VCPUS = 1

# The dict holds the credentials, which are not supposed to be printed
# to a tempest.conf when --test-accounts CLI parameter is used.
ALL_CREDENTIALS_KEYS = {
    "auth.admin_username": [],
    "auth.admin_password": [],
    "auth.admin_project_name": [],
    "auth.admin_domain_name": [],
    "identity.username": [],
    "identity.password": [],
    "identity.project_name": [],
    "identity.alt_username": [],
    "identity.alt_password": [],
    "identity.alt_project_name": [],
    "identity.admin_domain_name": [],
}
