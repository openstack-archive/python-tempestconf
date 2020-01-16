# Copyright 2016, 2018 Red Hat, Inc.
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

1. Default values provided by the tool.

2. Values using the file provided by the --deployer-input argument to the
script.
Some required options differ among deployed clouds but the right values cannot
be discovered by the user. The file used here could be created by an installer,
or manually if necessary.

3. Values provided in client's cloud config file or as an environment
variables, see documentation of openstacksdk
https://docs.openstack.org/openstacksdk/latest/

4. Values provided on the command line. These override all other values.

5. Discovery. Values that have not been provided in steps [2-4] will be
obtained by querying the cloud.
"""

import argparse
import logging
import os
import six
import sys

import openstack
from oslo_config import cfg
from six.moves import configparser

from config_tempest import accounts
from config_tempest.clients import ClientManager
from config_tempest import constants as C
from config_tempest.constants import LOG
from config_tempest.credentials import Credentials
from config_tempest.flavors import Flavors
from config_tempest import profile
from config_tempest.services.services import Services
from config_tempest.tempest_conf import TempestConf
from config_tempest.users import Users


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


def load_basic_defaults(conf):
    """Load basic default options into conf file.

    :type conf: TempestConf object
    """
    LOG.debug("Setting basic default values")
    default_values = {
        "DEFAULT": [
            ("debug", "true"),
            ("use_stderr", "false"),
            ("log_file", "tempest.log")
        ],
        "identity": [
            ("username", "demo"),
            ("password", "secrete"),
            ("project_name", "demo"),
            ("alt_username", "alt_demo"),
            ("alt_password", "secrete"),
            ("alt_project_name", "alt_demo"),
            ("disable_ssl_certificate_validation", "true")
        ],
        "scenario": [
            ("img_dir", "etc")
        ],
        "auth": [
            ("tempest_roles", "_member_"),
            ("admin_username", "admin"),
            ("admin_project_name", "admin"),
            ("admin_domain_name", "Default")
        ],
        "object-storage": [
            ("reseller_admin_role", "ResellerAdmin")
        ],
        "oslo-concurrency": [
            ("lock_path", "/tmp")
        ],
        "compute-feature-enabled": [
            # Default deployment does not use shared storage
            ("live_migration", "false"),
            ("live_migrate_paused_instances", "true"),
            ("preserve_ports", "true")
        ],
        "network-feature-enabled": [
            ("ipv6_subnet_attributes", "true")
        ]}

    for section in default_values.keys():
        if section != "DEFAULT" and not conf.has_section(section):
            conf.add_section(section)
        for key, value in default_values[section]:
            if not conf.has_option(section, key):
                conf.set(section, key, value)


def read_deployer_input(deployer_input_file, conf):
    """Read deployer-input file and set values in conf accordingly.

    :param deployer_input_file: Path to the deployer inut file
    :type deployer_input_file: String
    :param conf: TempestConf object
    """
    LOG.info("Adding options from deployer-input file '%s'",
             deployer_input_file)
    if six.PY3:
        deployer_input = configparser.ConfigParser()
    else:
        deployer_input = configparser.SafeConfigParser()
    deployer_input.read(deployer_input_file)
    for section in deployer_input.sections():
        # There are no deployer input options in DEFAULT
        for (key, value) in deployer_input.items(section):
            conf.set(section, key, value, priority=True)


def set_options(conf, deployer_input, non_admin, image_path, overrides=[],
                accounts_path=None, cloud_creds=None,
                no_default_deployer=False):
    """Set options in conf provided by different source.

    1. read the default values
    2. read a file provided by --deployer-input argument
    3. read default DEPLOYER_INPUT if --no-deployer-input is False and no
       deployer_input was passed
    4. set values from client's config (openstacksdk support) if provided
    5. set overrides - may override values which were set in the steps above

    :param conf: TempestConf object
    :param deployer_input: Path to the deployer inut file
    :type deployer_input: string
    :type non_admin: boolean
    :param image_path: An image to be uploaded to glance
    :type image_path: string
    :param overrides: list of tuples: [(section, key, value)]
    :type overrides: list
    :param accounts_path: A path where accounts.yaml is or will be created.
    :type accounts_path: string
    :param cloud_creds: Cloud credentials from client's config
    :type cloud_creds: dict
    """
    load_basic_defaults(conf)
    # image.image_path is a python-tempestconf option which defines which
    # image will be uploaded to glance
    conf.set('image', 'image_path', image_path)

    if deployer_input and os.path.isfile(deployer_input):
        LOG.info("Reading deployer input from file {}".format(
            deployer_input))
        read_deployer_input(deployer_input, conf)
    elif os.path.isfile(C.DEPLOYER_INPUT) and not no_default_deployer:
        LOG.info("Reading deployer input from file {}".format(
            C.DEPLOYER_INPUT))
        read_deployer_input(C.DEPLOYER_INPUT, conf)

    if non_admin:
        # non admin, so delete auth admin values which were set
        # in load_basic_defaults method
        conf.set("auth", "admin_username", "")
        conf.set("auth", "admin_project_name", "")
        conf.set("auth", "admin_password", "")
        conf.set("auth", "use_dynamic_credentials", "False", priority=True)

    # get and set auth data from client's config
    if cloud_creds:
        set_cloud_config_values(non_admin, cloud_creds, conf)

    if accounts_path:
        # new way for running using accounts file
        conf.set("auth", "use_dynamic_credentials", "False", priority=True)
        conf.set("auth", "test_accounts_file",
                 os.path.abspath(accounts_path))

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


def get_arg_parser():
    parser = argparse.ArgumentParser(__doc__)
    cloud_config = openstack.config.OpenStackConfig()
    cloud_config.register_argparse_arguments(parser, sys.argv)
    parser.add_argument('--create', action='store_true', default=False,
                        help="""Create Tempest resources
                                Make *python-tempestconf* to create Tempest
                                resources such as flavors needed for running
                                Tempest tests.""")
    parser.add_argument('--out', default="etc/tempest.conf",
                        help="""Output file
                                A name of the file where the discovered Tempest
                                configuration will be written to.""")
    parser.add_argument('--deployer-input', default=None,
                        help="""Path to deployer file
                                A file in the format of tempest.conf that will
                                override the default values. It is usually
                                created by an installer and contains
                                environment specific options.

                                The deployer-input file is an alternative to
                                providing key/value pairs. If there are also
                                key/value pairs they will be applied after the
                                deployer-input file.

                                If the option is **not defined** and
                                **--no-default-deployer** is **not used**,
                                python-tempestconf **will try** to look for the
                                file in `$HOME/tempest-deployer-input.conf`
                                location.""")
    parser.add_argument('--no-default-deployer', action='store_true',
                        default=False,
                        help="""Do not check for the default deployer input in
                                `$HOME/tempest-deployer-input.conf`""")
    parser.add_argument('overrides', nargs='*', default=[],
                        help="""Override options
                                Key value pairs used to hardcode values in
                                `tempest.conf`. The key is a section.key where
                                section is a section header in the conf file.
                                For example:
                                 $ discover-tempest-config \\
                                  identity.username myname \\
                                  identity.password mypass""")
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Print debugging information.')
    parser.add_argument('--verbose', '-v', action='store_true', default=False,
                        help='Print more information about the execution.')
    parser.add_argument('--no-rng', action='store_true', default=False,
                        help="""Create new flavors and upload images without
                                random number generator device.""")
    parser.add_argument('--non-admin', action='store_true', default=False,
                        help="""Simulate non-admin credentials.
                                When True, the credentials are used as
                                non-admin ones. No resources are created.""")
    parser.add_argument('--test-accounts', default=None, metavar='PATH',
                        help="""Tempest accounts.yaml file
                                Defines a path to a Tempest accounts.yaml
                                file.
                                For example:
                                 --test-accounts $HOME/tempest/accounts.yaml
                             """)
    parser.add_argument('--create-accounts-file', default=None,
                        metavar='PATH',
                        help="""Generate Tempest accounts file
                                Minimal accounts file will be created in the
                                specified path.
                                For example:
                                  --create-accounts-file $HOME/accounts.yaml
                             """)
    parser.add_argument('--profile', default=None, metavar='PATH',
                        help="""python-tempestconf's profile.yaml file
                                A file which contains definition of
                                python-tempestconf's arguments.
                                NOTE: If this argument is used, other
                                arguments cannot be defined!""")
    parser.add_argument('--generate-profile', default=None,
                        metavar='PATH',
                        help="""Generate a sample profile.yaml file.
                                A sample profile.yaml will be generated in the
                                specified path. After that python-tempestconf
                                ends.
                                For example:
                                  --generate-profile $HOME/profile.yaml
                             """)
    parser.add_argument('--image-disk-format', default=C.DEFAULT_IMAGE_FORMAT,
                        help="""A format of an image to be uploaded to glance.
                                Default is '%s'""" % C.DEFAULT_IMAGE_FORMAT)
    parser.add_argument('--image', default=C.DEFAULT_IMAGE,
                        help="""An image name/path/url to be uploaded to
                                glance if it's not already there. The name of
                                the image is the leaf name of the path. Default
                                is '%s'""" % C.DEFAULT_IMAGE)
    parser.add_argument('--flavor-min-mem', default=C.DEFAULT_FLAVOR_RAM,
                        type=int, help="""Specify minimum memory for new
                        flavours, default is '%s'.""" % C.DEFAULT_FLAVOR_RAM)
    parser.add_argument('--flavor-min-disk', default=C.DEFAULT_FLAVOR_DISK,
                        type=int, help="""Specify minimum disk size for new
                        flavours, default is '%s'.""" % C.DEFAULT_FLAVOR_DISK)
    parser.add_argument('--convert-to-raw', action='store_true', default=False,
                        help="""Convert images to raw format before uploading
                                to glance.""")
    parser.add_argument('--network-id',
                        help="""Specify which network with external connectivity
                                should be used by the tests.""")
    parser.add_argument('--append', action='append', default=[],
                        metavar="SECTION.KEY=VALUE[,VALUE]",
                        help="""Append values to tempest.conf
                                Key value pair to be appended to the
                                configuration file.
                                NOTE: Multiple values are supposed to be
                                divided by a COLON only, WITHOUT spaces.
                                For example:
                                 $ discover-tempest-config \\
                                  --append features.ext=tag[,tag-ext] \\
                                  --append section.ext=ext[,another-ext]
                             """)
    parser.add_argument('--remove', action='append', default=[],
                        metavar="SECTION.KEY=VALUE[,VALUE]",
                        help="""Remove values from tempest.conf
                                Key value pair to be removed from the
                                configuration file.
                                NOTE: Multiple values are supposed to be
                                divided by a COLON only, WITHOUT spaces.
                                For example:
                                 $ discover-tempest-config \\
                                  --remove identity.username=myname \\
                                  --remove feature-enabled.api_ext=http[,https]
                             """)
    return parser


def parse_arguments():
    parser = get_arg_parser()
    args = parser.parse_args()
    if args.create and args.non_admin:
        raise Exception("Options '--create' and '--non-admin' cannot be used"
                        " together, since creating" " resources requires"
                        " admin rights")
    if args.test_accounts and args.create_accounts_file:
        raise Exception("Options '--test-accounts' and "
                        "'--create-accounts-file' can't be used together.")
    args.overrides = parse_overrides(args.overrides)
    return args


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
                raise Exception("Missing dot. The option --remove has to "
                                "come in the format 'section.key=value[,value"
                                "]', but got '%s'." % argument)
            parsed[section] = values.split(',')
        else:
            # missing equal sign, all values in section.key will be deleted
            parsed[argument] = []
    return parsed


def parse_values_to_append(options):
    """Manual parsing of --append arguments.

    :param options: list of arguments following --append argument.
    :return: dictionary containing key paths with values to be added
    :rtype: dict
    """
    parsed = {}
    for argument in options:
        if len(argument.split('=')) == 2:
            section, values = argument.split('=')
            if len(section.split('.')) != 2:
                raise Exception("Missing dot. The option --append has to "
                                "come in the format 'section.key=value[,value"
                                "]', but got '%s'." % argument)
            if values == '':
                raise Exception("No values to append specified. The option "
                                "--append has to come in the format "
                                "'section.key=value[, value]', but got "
                                "'%s'" % values)
            parsed[section] = values.split(',')
        else:
            # missing equal sign, no values to add were specified, if a user
            # wants to just create a section, it can be done so via overrides
            raise Exception("Missing equal sign or more than just one found.")
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
    :param cloud_creds: auth data from openstacksdk
    :type cloud_creds: dict
    :param conf: TempestConf object
    """
    try:
        if non_admin:
            # Tempest doesn't have non-admin credentials, but we're gonna
            # keep them under identity for future usage
            conf.set('identity', 'username', cloud_creds['username'])
            conf.set('identity',
                     'project_name',
                     cloud_creds['project_name'])
            conf.set('identity', 'password', cloud_creds['password'])
        else:
            # admin credentials are under auth section
            conf.set('auth', 'admin_username', cloud_creds['username'])
            conf.set('auth',
                     'admin_project_name',
                     cloud_creds['project_name'])
            conf.set('auth', 'admin_password', cloud_creds['password'])
        conf.set('identity', 'uri', cloud_creds['auth_url'])

        if 'region_name' in cloud_creds:
            conf.set('identity', 'region', cloud_creds['region_name'])
    except cfg.NoSuchOptError:
        LOG.warning(
            'Could not load some identity options from cloud config file')


def get_cloud_creds(args_namespace):
    """Get cloud credentials based on argument namespace.

    If args contains --os-cloud argument, the method returns cloud
    credentials related to that cloud, otherwise, returns credentials
    of the current cloud.

    :type args_namespace: argparse.Namespace
    :return: cloud credentials
    :rtype: dict
    EXAMPLE: {'username': 'demo', 'project_name': 'demo',
              'user_domain_name': 'Default',
              'auth_url': 'http://172.16.52.8:5000/v3',
              'password': 'f0921edc3c2b4fc8', 'project_domain_name': 'Default'}
    """
    if args_namespace.os_cloud:
        cloud = openstack.connect(cloud=args_namespace.os_cloud)
    else:
        cloud = openstack.connect(argparse=args_namespace)

    cloud_creds = cloud.config.get_auth_args()
    region_name = cloud.config.config['region_name']

    if region_name:
        cloud_creds['region_name'] = region_name

    return cloud_creds


def config_tempest(**kwargs):
    # convert a list of remove values to a dict
    remove = parse_values_to_remove(kwargs.get('remove', []))
    add = parse_values_to_append(kwargs.get('append', []))
    set_logging(kwargs.get('debug', False), kwargs.get('verbose', False))

    accounts_path = kwargs.get('test_accounts')
    if kwargs.get('create_accounts_file') is not None:
        accounts_path = kwargs.get('create_accounts_file')
    conf = TempestConf(write_credentials=accounts_path is None)
    set_options(conf, kwargs.get('deployer_input'),
                kwargs.get('non_admin', False),
                kwargs.get('image_path', C.DEFAULT_IMAGE),
                kwargs.get('overrides', []),
                accounts_path,
                kwargs.get('cloud_creds'))

    credentials = Credentials(conf, not kwargs.get('non_admin', False))
    clients = ClientManager(conf, credentials)
    services = Services(clients, conf, credentials)

    if kwargs.get('create', False) and kwargs.get('test_accounts') is None:
        users = Users(clients.projects, clients.roles, clients.users, conf)
        users.create_tempest_users()

    if services.is_service(**{"type": "compute"}):
        flavors = Flavors(clients.flavors, kwargs.get('create', False), conf,
                          kwargs.get('flavor_min_mem', C.DEFAULT_FLAVOR_RAM),
                          kwargs.get('flavor_min_disk', C.DEFAULT_FLAVOR_DISK),
                          no_rng=kwargs.get('no_rng', False))
        flavors.create_tempest_flavors()

    if services.is_service(**{"type": "image"}):
        image = services.get_service('image')
        image.set_image_preferences(kwargs.get('image_disk_format',
                                               C.DEFAULT_IMAGE_FORMAT),
                                    kwargs.get('non_admin', False),
                                    no_rng=kwargs.get('no_rng', False),
                                    convert=kwargs.get('convert_to_raw',
                                                       False))
        image.create_tempest_images(conf)

    if services.is_service(**{"type": "network"}):
        network = services.get_service("network")
        network.create_tempest_networks(conf, kwargs.get('network_id'))

    services.post_configuration()
    services.set_supported_api_versions()
    services.set_service_extensions()

    if accounts_path is not None and kwargs.get('test_accounts') is None:
        LOG.info("Creating an accounts.yaml file in: %s", accounts_path)
        accounts.create_accounts_file(kwargs.get('create', False),
                                      accounts_path,
                                      conf)

    # remove all unwanted values if were specified
    if remove != {}:
        LOG.info("Removing configuration: %s", str(remove))
        conf.remove_values(remove)
    if add != {}:
        LOG.info("Adding configuration: %s", str(add))
        conf.append_values(add)
    out_path = kwargs.get('out', 'etc/tempest.conf')
    conf.write(out_path)


def main():
    args = parse_arguments()
    if args.generate_profile:
        profile.generate_profile(args, args.generate_profile)
        sys.exit(0)
    if args.profile:
        profile_args = profile.read_profile_file(args.profile)
        # update default args by values gained from the profile
        # Namespace can't be updated, so translate it to a dict first
        args_dict = vars(args)
        args_dict.update(profile_args)
        args = argparse.Namespace(**args_dict)
    cloud_creds = get_cloud_creds(args)
    config_tempest(
        append=args.append,
        cloud_creds=cloud_creds,
        convert_to_raw=args.convert_to_raw,
        create=args.create,
        create_accounts_file=args.create_accounts_file,
        debug=args.debug,
        deployer_input=args.deployer_input,
        flavor_min_mem=args.flavor_min_mem,
        flavor_min_disk=args.flavor_min_disk,
        image_disk_format=args.image_disk_format,
        image_path=args.image,
        network_id=args.network_id,
        non_admin=args.non_admin,
        no_rng=args.no_rng,
        os_cloud=args.os_cloud,
        out=args.out,
        overrides=args.overrides,
        remove=args.remove,
        test_accounts=args.test_accounts,
        verbose=args.verbose
    )


if __name__ == "__main__":
    main()
