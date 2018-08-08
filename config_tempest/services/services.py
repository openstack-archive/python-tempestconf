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


from six.moves import urllib

from config_tempest import constants as C
from config_tempest.services.base import Service
from config_tempest.services import boto
from config_tempest.services import ceilometer
from config_tempest.services.compute import ComputeService
from config_tempest.services import horizon
from config_tempest.services.identity import IdentityService
from config_tempest.services.image import ImageService
from config_tempest.services.network import NetworkService
from config_tempest.services.object_storage import ObjectStorageService
from config_tempest.services.octavia import LoadBalancerService
from config_tempest.services import volume


service_dict = {'compute': ComputeService,
                'image': ImageService,
                'network': NetworkService,
                'object-store': ObjectStorageService,
                'volumev3': volume.VolumeService,
                'identity': IdentityService,
                'ec2': boto.Ec2Service,
                's3': boto.S3Service,
                'load-balancer': LoadBalancerService}


class Services(object):
    def __init__(self, clients, conf, creds):
        self._clients = clients
        self._conf = conf
        self._creds = creds
        self._ssl_validation = creds.disable_ssl_certificate_validation
        self._region = clients.identity_region
        self._services = []
        self.set_catalog_and_url()

        self.discover()

    def discover(self):
        token, auth_data = self._clients.auth_provider.get_auth()

        for entry in auth_data[self.service_catalog]:
            name = entry['type']
            url = self.parse_endpoints(self.get_endpoints(entry), name)

            service_class = self.get_service_class(name)
            service = service_class(name, url, token, self._ssl_validation,
                                    self._clients.get_service_client(name))
            # discover extensions of the service
            service.set_extensions()
            # discover versions of the service
            service.set_versions()
            self.merge_exts_multiversion_service(service)

            # default tempest options
            service.set_default_tempest_options(self._conf)

            self._services.append(service)

    def merge_exts_multiversion_service(self, service):
        """Merges extensions of a service given by its name

        Looking for extensions from all versions of the service
        defined by name and merges them to that provided service.

        :param service: Service object
        """
        versions = service.get_supported_versions()
        service_name = service.get_unversioned_service_name()
        services_lst = []
        for v in versions:
            if self.is_service(service_name + v):
                services_lst.append(self.get_service(service_name + v))
        services_lst.append(service)
        service.extensions = self.merge_extensions(services_lst)

    def get_endpoints(self, entry):
        for ep in entry['endpoints']:
            if self._creds.api_version == 3:
                if (ep['region'] == self._region and
                        ep['interface'] == 'public'):
                    return ep
            else:
                if ep['region'] == self._region:
                    return ep
        try:
            return entry['endpoints'][0]
        except IndexError:
            return []

    def set_catalog_and_url(self):
        if self._creds.api_version == 3:
            self.service_catalog = 'catalog'
            self.public_url = 'url'
        else:
            self.service_catalog = 'serviceCatalog'
            self.public_url = 'publicURL'

    def parse_endpoints(self, ep, name):
        """Parse an endpoint(s).

        :param ep: endpoint(s)
        :type ep: dict or list in case of no endpoints
        :param name: name of a service
        :type name: string
        :return: url
        :rtype: string
        """
        # endpoint list can be empty
        if len(ep) == 0:
            url = ""
            C.LOG.info("Service %s has no endpoints", name)
        else:
            url = ep[self.public_url]
        if 'identity' in urllib.parse.urlparse(url).path:
            url = self.edit_identity_url(ep[self.public_url])
        return url

    def edit_identity_url(self, url):
        """A port and identity version are added to url if contains 'identity'

        :param url: url address of an endpoint
        :type url: string
        :rtype: string
        """
        # self._clients.auth_provider.auth_url stores identity.uri(_v3) value
        # from TempestConf
        port = urllib.parse.urlparse(self._clients.auth_provider.auth_url).port
        if port is None:
            port = ""
        else:
            port = ":" + str(port)
        replace_text = port + "/identity/" + self._creds.identity_version
        return url.replace("/identity", replace_text)

    def get_service_class(self, name):
        """Returns class name by the service name

        :param name: Codename of a service
        :type name: string
        :return: Class name of the service
        :rtype: string
        """
        return service_dict.get(name, Service)

    def get_service(self, name):
        """Finds and returns a service object

        :param name: Codename of a service
        :type name: string
        :return: Service object
        """
        for service in self._services:
            if service.name == name:
                return service
        return None

    def is_service(self, name):
        """Returns true if a service is available, false otherwise

        :param name: Codename of a service
        :type name: string
        :rtype: boolean
        """
        if self.get_service(name) is None:
            return False
        return True

    def set_service_availability(self):
        # check if volume service is disabled
        if self._conf.has_option('services', 'volume'):
            if not self._conf.getboolean('services', 'volume'):
                C.SERVICE_NAMES.pop('volume')
        # check availability of volume backup service
        volume.check_volume_backup_service(self._conf,
                                           self._clients.volume_client,
                                           self.is_service("volumev3"))

        ceilometer.check_ceilometer_service(self._conf,
                                            self._clients.service_client)

        horizon.configure_horizon(self._conf)

        for service, codename in C.SERVICE_NAMES.iteritems():
            # ceilometer is still transitioning from metering to telemetry
            if service == 'telemetry' and self.is_service('metering'):
                service = 'metering'
            available = str(self.is_service(service))
            self._conf.set('service_available', codename, available)

        # TODO(arxcruz): Remove this once/if we get the following reviews
        # merged in all branches supported by tempestconf, or once/if
        # tempestconf do not support anymore the OpenStack release where
        # those patches are not available.
        # https://review.openstack.org/#/c/492526/
        # https://review.openstack.org/#/c/492525/

        if self.is_service('alarming'):
            self._conf.set('service_available', 'aodh', 'True')
            self._conf.set('service_available', 'aodh_plugin', 'True')

        # TODO(arxcruz): This should be set in compute service, not here,
        # however, it requires a refactor in the code, which is not our
        # goal right now
        self._conf.set('compute-feature-enabled',
                       'attach_encrypted_volume',
                       str(self.is_service('key-manager')))

    def set_supported_api_versions(self):
        # set supported API versions for services with more of them
        for service in self._services:
            versions = service.get_versions()
            supported_versions = service.get_supported_versions()
            if versions:
                section = service.get_feature_name() + '-feature-enabled'
                for s_version in supported_versions:
                    is_supported = any(s_version in item
                                       for item in versions)
                    self._conf.set(
                        section, 'api_' + s_version, str(is_supported))

    def merge_extensions(self, service_objects):
        """Merges extensions from all provided service objects

        :param service_objects:
        :type service_objects: list
        :return: Merged extensions
        :rtype: list
        """
        extensions = []
        for o in service_objects:
            extensions += o.extensions
        return extensions

    def set_service_extensions(self):
        postfix = "-feature-enabled"
        try:
            keystone_v3_support = self._conf.getboolean('identity' + postfix,
                                                        'api_v3')
        except ValueError:
            keystone_v3_support = False
        if keystone_v3_support:
            self.get_service('identity').set_identity_v3_extensions()

        for service in self._services:
            ext_key = service.get_service_extension_key()
            if ext_key:
                extensions = ','.join(service.get_extensions())
                service_name = service.get_feature_name()
                self._conf.set(service_name + postfix, ext_key, extensions)
