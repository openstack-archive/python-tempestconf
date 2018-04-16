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

DEFAULTS_FILE = os.path.join(TEMPEST_WORKSPACE, "etc",
                             "default-overrides.conf")
DEFAULT_IMAGE = ("http://download.cirros-cloud.net/0.3.5/"
                 "cirros-0.3.5-x86_64-disk.img")
DEFAULT_IMAGE_FORMAT = 'qcow2'

# services and their codenames
SERVICE_NAMES = {
    'baremetal': 'ironic',
    'compute': 'nova',
    'database': 'trove',
    'data-processing': 'sahara',
    'image': 'glance',
    'network': 'neutron',
    'object-store': 'swift',
    'orchestration': 'heat',
    'share': 'manila',
    'telemetry': 'ceilometer',
    'volume': 'cinder',
    'messaging': 'zaqar',
    'metric': 'gnocchi',
    'event': 'panko',
}

# what API versions could the service have and should be enabled/disabled
# depending on whether they get discovered as supported. Services with only one
# version don't need to be here, neither do service versions that are not
# configurable in tempest.conf
SERVICE_VERSIONS = {
    'image': {'supported_versions': ['v1', 'v2'], 'catalog': 'image'},
    'identity': {'supported_versions': ['v2', 'v3'], 'catalog': 'identity'},
    'volume': {'supported_versions': ['v2', 'v3'], 'catalog': 'volumev3'}
}

# Keep track of where the extensions are saved for that service.
# This is necessary because the configuration file is inconsistent - it uses
# different option names for service extension depending on the service.
SERVICE_EXTENSION_KEY = {
    'compute': 'api_extensions',
    'object-store': 'discoverable_apis',
    'network': 'api_extensions',
    'volume': 'api_extensions',
    'identity': 'api_extensions'
}
