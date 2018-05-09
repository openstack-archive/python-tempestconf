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
"""
This script will generate the etc/tempest.conf file by applying a series of
specified options in the following order:

1. Values from etc/default-overrides.conf, if present. This file will be
provided by the distributor of the tempest code, a distro for example, to
specify defaults that are different than the generic defaults for tempest.

2. Values using the file provided by the --deployer-input argument to the
script.
Some required options differ among deployed clouds but the right values cannot
be discovered by the user. The file used here could be created by an installer,
or manually if necessary.

3. Values provided in client's cloud config file or as an environment
variables, see documentation of os-client-config
https://docs.openstack.org/developer/os-client-config/

4. Values provided on the command line. These override all other values.

5. Discovery. Values that have not been provided in steps [2-4] will be
obtained by querying the cloud.
"""

import argparse
import ConfigParser
import logging
import os
import sys

from clients import ClientManager
import constants as C
from constants import LOG
from credentials import Credentials
from flavors import Flavors
import os_client_config
from oslo_config import cfg
from services import boto
from services import ceilometer
from services.horizon import configure_horizon
from services.services import Services
from services import volume
import tempest_conf
from users import Users


def set_logging(debug, verbose):
    """Set logging based on the arguments.

    :type debug: Boolean
    :type verbose: Boolean
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=log_format)
    if debug:
        LOG.setLevel(logging.DEBUG)
    elif verbose:
        LOG.setLevel(logging.INFO)


def read_deployer_input(deployer_input_file, conf):
    """Read deployer-input file and set values in conf accordingly.

    :param deployer_input_file: Path to the deployer inut file
    :type deployer_input_file: String
    :param conf: TempestConf object
    """
    LOG.info("Adding options from deployer-input file '%s'",
             deployer_input_file)
    deployer_input = ConfigParser.SafeConfigParser()
    deployer_input.read(deployer_input_file)
    for section in deployer_input.sections():
        # There are no deployer input options in DEFAULT
        for (key, value) in deployer_input.items(section):
            conf.set(section, key, value, priority=True)


def set_options(conf, deployer_input, non_admin, overrides=[],
                test_accounts=None, cloud_creds=None):
    """Set options in conf provided by different source.

    1. read the default values in default-overrides file
    2. read a file provided by --deployer-input argument
    3. set values from client's config (os-client-config support) if provided
    4. set overrides - may override values which were set in the steps above

    :param conf: TempestConf object
    :param deployer_input: Path to the deployer inut file
    :type deployer_input: string
    :type non_admin: boolean
    :param overrides: list of tuples: [(section, key, value)]
    :type overrides: list
    :param test_accounts: Path to the accounts.yaml file
    :type test_accounts: string
    :param cloud_creds: Cloud credentials from client's config
    :type cloud_creds: dict
    """
    if os.path.isfile(C.DEFAULTS_FILE):
        LOG.info("Reading defaults from file '%s'", C.DEFAULTS_FILE)
        conf.read(C.DEFAULTS_FILE)

    if deployer_input and os.path.isfile(deployer_input):
        read_deployer_input(deployer_input, conf)

    if non_admin:
        # non admin, so delete auth admin values which were set
        # from default-overides.conf file
        conf.set("auth", "admin_username", "")
        conf.set("auth", "admin_project_name", "")
        conf.set("auth", "admin_password", "")
        # To maintain backward compatibilty
        # Moved to auth
        conf.set("identity", "admin_username", "")
        # To maintain backward compatibility
        # renamed as admin_project_name in auth section
        conf.set("identity", "admin_tenant_name", "")
        # To maintain backward compatibility
        # Moved to auth
        conf.set("identity", "admin_password", "")
        conf.set("auth", "use_dynamic_credentials", "False")

    # get and set auth data from client's config
    if cloud_creds:
        set_cloud_config_values(non_admin, cloud_creds, conf)

    if test_accounts:
        # new way for running using accounts file
        conf.set("auth", "use_dynamic_credentials", "False")
        conf.set("auth", "test_accounts_file",
                 os.path.abspath(test_accounts))

    # set overrides - values specified in CLI
    for section, key, value in overrides:
        conf.set(section, key, value, priority=True)

    uri = conf.get("identity", "uri")
    if "v3" in uri:
        conf.set("identity", "auth_version", "v3")
        conf.set("identity", "uri_v3", uri)
    else:
        # TODO(arxcruz) make a check if v3 is enabled
        conf.set("identity", "uri_v3", uri.replace("v2.0", "v3"))


def parse_arguments():
    cloud_config = os_client_config.OpenStackConfig()
    parser = argparse.ArgumentParser(__doc__)
    cloud_config.register_argparse_arguments(parser, sys.argv)
    parser.add_argument('--create', action='store_true', default=False,
                        help='create default tempest resources')
    parser.add_argument('--out', default="etc/tempest.conf",
                        help='the tempest.conf file to write')
    parser.add_argument('--deployer-input', default=None,
                        help="""A file in the format of tempest.conf that will
                                override the default values. The
                                deployer-input file is an alternative to
                                providing key/value pairs. If there are also
                                key/value pairs they will be applied after the
                                deployer-input file.
                        """)
    parser.add_argument('overrides', nargs='*', default=[],
                        help="""key value pairs to modify. The key is
                                section.key where section is a section header
                                in the conf file.
                                For example: identity.username myname
                                 identity.password mypass""")
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Print debugging information')
    parser.add_argument('--verbose', '-v', action='store_true', default=False,
                        help='Print more information about the execution')
    parser.add_argument('--non-admin', action='store_true', default=False,
                        help='Run without admin creds')
    parser.add_argument('--test-accounts', default=None, metavar='PATH',
                        help='Use accounts from accounts.yaml')
    parser.add_argument('--image-disk-format', default=C.DEFAULT_IMAGE_FORMAT,
                        help="""a format of an image to be uploaded to glance.
                                Default is '%s'""" % C.DEFAULT_IMAGE_FORMAT)
    parser.add_argument('--image', default=C.DEFAULT_IMAGE,
                        help="""an image to be uploaded to glance. The name of
                                the image is the leaf name of the path which
                                can be either a filename or url. Default is
                                '%s'""" % C.DEFAULT_IMAGE)
    parser.add_argument('--network-id',
                        help="""The ID of an existing network in our openstack
                                instance with external connectivity""")
    parser.add_argument('--remove', action='append', default=[],
                        metavar="SECTION.KEY=VALUE[,VALUE]",
                        help="""key value pair to be removed from
                                configuration file.
                                For example: --remove identity.username=myname
                                --remove feature-enabled.api_ext=http,https""")

    args = parser.parse_args()
    if args.create and args.non_admin:
        raise Exception("Options '--create' and '--non-admin' cannot be used"
                        " together, since creating" " resources requires"
                        " admin rights")
    args.overrides = parse_overrides(args.overrides)
    cloud = cloud_config.get_one_cloud(argparse=args)
    return cloud


def parse_values_to_remove(options):
    """Manual parsing of remove arguments.

    :param options: list of arguments following --remove argument
    :return: dictionary containing key paths with values to be removed
    :rtype: dict
    EXAMPLE: {'identity.username': [myname],
              'identity-feature-enabled.api_extensions': [http, https]}
    """
    parsed = {}
    for argument in options:
        if len(argument.split('=')) == 2:
            section, values = argument.split('=')
            if len(section.split('.')) != 2:
                raise Exception("Missing dot. The option --remove has to"
                                "come in the format 'section.key=value,"
                                " but got '%s'." % (argument))
            parsed[section] = values.split(',')
        else:
            # missing equal sign, all values in section.key will be deleted
            parsed[argument] = []
    return parsed


def parse_overrides(overrides):
    """Manual parsing of positional arguments.

    :param overrides: list of section.keys and values to override, example:
               ['section.key', 'value', 'section.key', 'value']
    :return: list of tuples, example: [('section', 'key', 'value'), ...]
    :rtype: list
    """
    if len(overrides) % 2 != 0:
        raise Exception("An odd number of override options was found. The"
                        " overrides have to be in 'section.key value' format.")
    i = 0
    new_overrides = []
    while i < len(overrides):
        section_key = overrides[i].split('.')
        value = overrides[i + 1]
        if len(section_key) != 2:
            raise Exception("Missing dot. The option overrides has to come in"
                            " the format 'section.key value', but got '%s'."
                            % (overrides[i] + ' ' + value))
        section, key = section_key
        new_overrides.append((section, key, value))
        i += 2
    return new_overrides


def set_cloud_config_values(non_admin, cloud_creds, conf):
    """Set values from client's cloud config file.

    Set admin and non-admin credentials and uri from cloud credentials.
    Note: the values may be later overridden by values specified in CLI.

    :type non_admin: Boolean
    :param cloud_creds: auth data from os-client-config
    :type cloud_creds: dict
    :param conf: TempestConf object
    """
    try:
        if non_admin:
            conf.set('identity', 'username', cloud_creds['username'])
            conf.set('identity',
                     'tenant_name',
                     cloud_creds['project_name'])
            conf.set('identity', 'password', cloud_creds['password'])
        else:
            conf.set('identity', 'admin_username', cloud_creds['username'])
            conf.set('identity',
                     'admin_tenant_name',
                     cloud_creds['project_name'])
            conf.set('identity', 'admin_password', cloud_creds['password'])
        conf.set('identity', 'uri', cloud_creds['auth_url'])

    except cfg.NoSuchOptError:
        LOG.warning(
            'Could not load some identity options from cloud config file')


def main():
    args = parse_arguments()
    args.remove = parse_values_to_remove(args.remove)
    set_logging(args.debug, args.verbose)

    conf = tempest_conf.TempestConf()
    cloud_creds = args.config.get('auth')
    set_options(conf, args.deployer_input, args.non_admin,
                args.overrides, args.test_accounts, cloud_creds)

    credentials = Credentials(conf, not args.non_admin)
    clients = ClientManager(conf, credentials)
    services = Services(clients, conf, credentials)

    if args.create and args.test_accounts is None:
        users = Users(clients.tenants, clients.roles, clients.users, conf)
        users.create_tempest_users(services.is_service('orchestration'))
    flavors = Flavors(clients.flavors, args.create, conf)
    flavors.create_tempest_flavors()

    image = services.get_service('image')
    image.set_image_preferences(args.create, args.image,
                                args.image_disk_format)
    image.create_tempest_images(conf)

    has_neutron = services.is_service("network")
    network = services.get_service("network")
    network.create_tempest_networks(has_neutron, conf, args.network_id)

    services.set_service_availability()
    services.set_supported_api_versions()
    services.set_service_extensions()
    volume.check_volume_backup_service(conf, clients.volume_client,
                                       services.is_service("volumev3"))
    ceilometer.check_ceilometer_service(conf, clients.service_client)
    boto.configure_boto(conf,
                        s3_service=services.get_service("s3"))
    identity = services.get_service('identity')
    identity.configure_keystone_feature_flags(conf)
    configure_horizon(conf)

    # remove all unwanted values if were specified
    if args.remove != {}:
        LOG.info("Removing configuration: %s", str(args.remove))
        conf.remove_values(args.remove)
    LOG.info("Creating configuration file %s", os.path.abspath(args.out))
    with open(args.out, 'w') as f:
        conf.write(f)


if __name__ == "__main__":
    main()