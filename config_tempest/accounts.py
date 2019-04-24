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

import yaml


def create_accounts_file(create, accounts_path, conf):
    if create:
        section = 'auth'
        prefix = 'admin_'
    else:
        section = 'identity'
        prefix = ''
    write_accounts_file(accounts_path,
                        conf.get(section, prefix + 'username'),
                        conf.get(section, prefix + 'password'),
                        conf.get(section, prefix + 'project_name'))


def write_accounts_file(path, username, password, project_name):
    """Creates a minimal accounts.yaml file.

    Dumps provided credentials in a yaml format.

    :type path: string
    :type username: string
    :type password: string
    :type project_name: string
    """
    comments = "# A minimal accounts.yaml file\n" \
               "# Will likely not work with swift, since additional\n" \
               "# roles are required. For more documentation see:\n" \
               "# https://opendev.org/openstack/tempest/src/branch/master/" \
               "etc/accounts.yaml.sample\n\n"
    accounts = []
    accounts.append({
        'username': username,
        'project_name': project_name,
        'password': password
    })
    with open(path, 'w') as outfile:
        for line in comments:
            outfile.write(line)
        yaml.safe_dump(accounts, outfile, default_flow_style=False)
