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

from tempest.lib import exceptions
from tempest.lib.services.compute import flavors_client
from tempest.lib.services.compute import hosts_client
from tempest.lib.services.compute import servers_client
from tempest.lib.services.identity.v2 import identity_client
from tempest.lib.services.identity.v2 import roles_client
from tempest.lib.services.identity.v2 import tenants_client
from tempest.lib.services.identity.v2 import users_client
from tempest.lib.services.identity.v3  \
    import identity_client as identity_v3_client
from tempest.lib.services.identity.v3 import projects_client
from tempest.lib.services.identity.v3 import roles_client as roles_v3_client
from tempest.lib.services.identity.v3 import services_client as s_client
from tempest.lib.services.identity.v3 import users_client as users_v3_client
from tempest.lib.services.image.v2 import images_client
from tempest.lib.services.network import networks_client
from tempest.lib.services.object_storage import account_client
try:
    # Since Rocky, volume.v3.services_client is the default
    from tempest.lib.services.volume.v3 import services_client
except ImportError:
    # For backward compatibility
    from tempest.lib.services.volume.v2 import services_client


class ProjectsClient(object):
    """The class is a wrapper for managing projects/tenants.

    It instantiates tempest projects_client and provides methods for creating
    and finding projects (identity version v3)/tenants (identity version v2).
    """
    def __init__(self, auth, catalog_type, identity_region, endpoint_type,
                 identity_version, **default_params):
        self.identity_version = identity_version
        if self.identity_version == "v2":
            self.project_class = tenants_client.TenantsClient
        else:
            self.project_class = projects_client.ProjectsClient
        self.client = self.project_class(auth, catalog_type, identity_region,
                                         endpoint_type, **default_params)

    def get_project_by_name(self, project_name):
        if self.identity_version == "v2":
            projects = self.client.list_tenants()['tenants']
        else:
            projects = self.client.list_projects()['projects']
        for project in projects:
            if project['name'] == project_name:
                return project
        raise exceptions.NotFound(
            'No such project/tenant (%s) in %s' % (project_name, projects))

    def create_project(self, name, description):
        if self.identity_version == "v2":
            self.client.create_tenant(name=name, description=description)
        else:
            self.client.create_project(name=name, description=description)


class ClientManager(object):
    """Manager of various OpenStack API clients.

    Connections to clients are created on-demand, i.e. the client tries to
    connect to the server only when it's being requested.
    """
    def __init__(self, conf, creds):
        """Init method of ClientManager.

        :param conf: TempestConf object
        :param creds: Credentials object
        """
        self.identity_region = creds.identity_region
        self.auth_provider = creds.get_auth_provider()

        default_params = self._get_default_params(conf)
        compute_params = self._get_compute_params(conf)
        compute_params.update(default_params)

        catalog_type = conf.get_defaulted('identity', 'catalog_type')

        self.identity = self.get_identity_client(
            creds.identity_version,
            catalog_type,
            default_params)

        self.projects = ProjectsClient(
            self.auth_provider,
            conf.get_defaulted('identity', 'catalog_type'),
            self.identity_region,
            'publicURL',
            creds.identity_version,
            **default_params)

        self.set_roles_client(
            auth=self.auth_provider,
            identity_version=creds.identity_version,
            catalog_type=catalog_type,
            endpoint_type='publicURL',
            default_params=default_params)

        self.hosts_client = hosts_client.HostsClient(
            self.auth_provider,
            conf.get_defaulted('compute', 'catalog_type'),
            self.identity_region,
            **default_params)

        self.accounts = account_client.AccountClient(
            self.auth_provider,
            conf.get_defaulted('object-storage', 'catalog_type'),
            self.identity_region,
            **default_params)

        self.set_users_client(
            auth=self.auth_provider,
            identity_version=creds.identity_version,
            catalog_type=catalog_type,
            endpoint_type='publicURL',
            default_params=default_params)

        self.images = images_client.ImagesClient(
            self.auth_provider,
            conf.get_defaulted('image', 'catalog_type'),
            self.identity_region,
            **default_params)

        self.servers = servers_client.ServersClient(self.auth_provider,
                                                    **compute_params)
        self.flavors = flavors_client.FlavorsClient(self.auth_provider,
                                                    **compute_params)

        self.service_client = s_client.ServicesClient(
            self.auth_provider,
            conf.get_defaulted('identity', 'catalog_type'),
            self.identity_region,
            **default_params)

        self.volume_client = services_client.ServicesClient(
            self.auth_provider,
            conf.get_defaulted('volume', 'catalog_type'),
            self.identity_region,
            **default_params)

        self.networks = None

        def create_neutron_client():
            if self.networks is None:
                self.networks = networks_client.NetworksClient(
                    self.auth_provider,
                    conf.get_defaulted('network', 'catalog_type'),
                    self.identity_region,
                    endpoint_type=conf.get_defaulted('network',
                                                     'endpoint_type'),
                    **default_params)
            return self.networks

        self.get_neutron_client = create_neutron_client

        # Set admin project id needed for keystone v3 tests.
        if creds.admin:
            project = self.projects.get_project_by_name(creds.project_name)
            conf.set('auth', 'admin_project_id', project['id'])

    def _get_default_params(self, conf):
        default_params = {
            'disable_ssl_certificate_validation':
                conf.get_defaulted('identity',
                                   'disable_ssl_certificate_validation'),
            'ca_certs': conf.get_defaulted('identity', 'ca_certificates_file')
        }
        return default_params

    def _get_compute_params(self, conf):
        compute_params = {
            'service': conf.get_defaulted('compute', 'catalog_type'),
            'region': self.identity_region,
            'endpoint_type': conf.get_defaulted('compute', 'endpoint_type')
        }
        return compute_params

    def get_identity_client(self, identity_version, catalog_type,
                            default_params):
        """Obtain identity client.

        :type identity_version: string
        :type catalog_type: string
        :type default_params: dict
        """
        if "v3" in identity_version:
            return identity_v3_client.IdentityClient(
                self.auth_provider,
                catalog_type,
                self.identity_region, endpoint_type='publicURL',
                **default_params)
        else:
            return identity_client.IdentityClient(
                self.auth_provider,
                catalog_type,
                self.identity_region, endpoint_type='publicURL',
                **default_params)

    def get_service_client(self, service_name):
        """Returns name of the service's client.

        :type service_name: string
        :rtype: client object or None when the client doesn't exist
        """
        # TODO(arxcruz): This function is under used, it should return
        # a dictionary of all services for a particular client, for
        # example, we need hosts_client and flavors_client for compute
        # should return {'hosts': self.hosts_client, 'flavors': self.flavors }
        # and so on.
        if service_name == "image":
            return self.images
        elif service_name in ["network", "object-store"]:
            # return whole ClientManager object because NetworkService
            # currently needs to have an access to get_neutron/nova_client
            # methods which are chosen according to neutron presence
            return self
        elif service_name == "compute":
            return self.hosts_client
        elif "volume" in service_name:
            return self.volume_client
        elif service_name == "metering":
            return self.service_client
        else:
            return None

    def set_users_client(self, auth, identity_version, catalog_type,
                         endpoint_type, default_params):
        """Sets users client.

        :param auth: auth provider
        :type auth: auth.KeystoneV2AuthProvider (or V3)
        :type identity_version: string
        :type catalog_type: string
        :type endpoint_type: string
        :type default_params: dict
        """
        users_class = users_client.UsersClient
        if "v3" in identity_version:
            users_class = users_v3_client.UsersClient

        self.users = users_class(
            auth,
            catalog_type,
            self.identity_region,
            endpoint_type=endpoint_type,
            **default_params)

    def set_roles_client(self, auth, identity_version, catalog_type,
                         endpoint_type, default_params):
        """Sets roles client.

        :param auth: auth provider
        :type auth: auth.KeystoneV2AuthProvider (or V3)
        :type identity_version: string
        :type catalog_type: string
        :type endpoint_type: string
        :type default_params: dict
        """
        roles_class = roles_client.RolesClient
        if "v3" in identity_version:
            roles_class = roles_v3_client.RolesClient

        self.roles = roles_class(
            auth,
            catalog_type,
            self.identity_region,
            endpoint_type=endpoint_type,
            **default_params)
