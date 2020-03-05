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


def _convert_remove_append(options):
    """Convert append and remove dicts read from .yaml file.

    :param options: {'section.key': 'value1,value2', ...}
    :type options: dict
    :return: ['section.key=value1,value2', ...]
    :rtype: list
    """
    converted = []
    for key in options:
        v = options[key]
        if isinstance(v, list):
            v = ','.join(v)
        converted.append(key + "=" + v)
    return converted


def _read_yaml_file(path):
    """Read a .yaml file.

    :param path: path to the profile.yaml file
    :type path: string
    :return: profile arguments
    :rtype: dict
    """
    with open(path, 'r') as stream:
        return yaml.safe_load(stream)


def read_profile_file(path):
    """Read python-tempestconf arguments from a .yaml file.

    :param path: path to the profile.yaml file
    :type path: string
    :return: profile arguments
    :rtype: dict
    """
    profile_args = _read_yaml_file(path)
    # convert overrides, to a list of tuples (s, k, v)
    overrides = []
    if 'overrides' in profile_args:
        for key in profile_args['overrides']:
            s, k = key.split('.')
            v = profile_args['overrides'][key]
            if isinstance(v, list):
                v = ','.join(v)
            overrides.append((s, k, str(v)))
    profile_args['overrides'] = overrides
    # convert remove
    remove = []
    if 'remove' in profile_args:
        remove = _convert_remove_append(profile_args['remove'])
    profile_args['remove'] = remove
    # convert append values
    append = []
    if 'append' in profile_args:
        append = _convert_remove_append(profile_args['append'])
    profile_args['append'] = append
    return profile_args


def generate_profile(args, path):
    """Generates a sample profile.yaml file.

    :type args: argparse.Namespace
    :param path: Specifies where the sample file will be generated in.
    :type path: string
    """
    iterable_args = vars(args)
    # pop following arguments as they are written
    # more detailed to the file below
    iterable_args.pop('append')
    iterable_args.pop('overrides')
    iterable_args.pop('remove')
    # pop profile as that shouldn't be in a profile.yaml
    iterable_args.pop('profile')
    with open(path, 'w') as outfile:
        yaml.safe_dump(iterable_args, outfile, default_flow_style=False)
        outfile.write("""append: {}
  #identity.username: username
  #compute-feature-enabled.api_extensions:
  #  - dvr
  #  - extension
overrides: {}
  #identity.username: username
  #identity.password:
  #  - my_password
  #compute-feature-enabled.api_extensions:
  #  - dvr
  #  - extension
remove: {}
  #identity.username: username
  #compute-feature-enabled.api_extensions:
  #  - dvr
  #  - extension
""")
