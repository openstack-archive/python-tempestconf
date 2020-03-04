# Copyright 2013 Red Hat, Inc.
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

import json
import re
import urllib3

from six.moves import urllib

from config_tempest.constants import LOG

from tempest.lib import exceptions


MULTIPLE_SLASH = re.compile(r'/+')


class ServiceError(Exception):
    pass


class Service(object):
    def __init__(self, name, s_type, service_url, token,
                 disable_ssl_validation, client=None):
        self.name = name
        self.s_type = s_type
        self.service_url = service_url
        self.headers = {'Accept': 'application/json', 'X-Auth-Token': token}
        self.disable_ssl_validation = disable_ssl_validation
        self.client = client

        self.extensions = []
        self.versions = []
        self.versions_body = {'versions': []}

    def do_get(self, url, top_level=False, top_level_path=""):
        parts = list(urllib.parse.urlparse(url))
        # 2 is the path offset
        if top_level:
            parts[2] = '/' + top_level_path

        parts[2] = MULTIPLE_SLASH.sub('/', parts[2])
        url = urllib.parse.urlunparse(parts)

        try:
            if self.disable_ssl_validation:
                urllib3.disable_warnings()
                http = urllib3.PoolManager(cert_reqs='CERT_NONE')
            else:
                http = urllib3.PoolManager()
            r = http.request('GET', url, headers=self.headers)
        except Exception as e:
            LOG.error("Request on service '%s' with url '%s' failed",
                      self.s_type, url)
            raise e

        if r.status == 403:
            raise exceptions.Forbidden("Request on service '%s' with url '%s' "
                                       "failed with code 403" % (self.s_type,
                                                                 url))

        if r.status >= 400:
            raise ServiceError("Request on service '%s' with url '%s' failed"
                               " with code %d" % (self.s_type, url, r.status))
        return r.data.decode('utf-8')

    def set_extensions(self):
        self.extensions = []

    def set_versions(self):
        self.versions = []

    def set_availability(self, conf, available):
        """Sets service's availability.

        The services's codename will be set to desired value under
        [service_available] section in tempest.conf during the services
        discovery process.
        """
        try:
            conf.set('service_available', self.get_codename(), str(available))
        except NotImplementedError:
            pass

    def get_extensions(self):
        return self.extensions

    @staticmethod
    def get_service_type():
        """Return the service type.

        This returns a list because you can have services with more types,
        like volume, volumev2, volumev3.
        """
        return []

    def get_versions(self):
        """Return the versions available for each service.

        This doesn't mean tempestconf supports all these versions. Only that
        the service has these api versions enabled.
        """
        return self.versions

    def set_default_tempest_options(self, conf):
        pass

    def get_supported_versions(self):
        """Return the versions supported by tempestconf.

        The server might have older or newer versions that could not be
        supported by tempestconf.
        """
        return []

    @staticmethod
    def get_codename():
        """Return the service_available name of the service.

        This name is used when setting service availability in
        set_availability method. If the method is not implemented, service
        availability is not set.
        """
        raise NotImplementedError

    def get_feature_name(self):
        """Return the name of service used in <service>-feature-enabled.

        Some services have the -feature-enabled option in tempest, that
        diverges from the service name. The main example is object-store
        service where the <service>-feature-enabled is object-storage.
        """
        return self.s_type

    def get_service_extension_key(self):
        """Return the extension key for a particular service"""
        return None

    def get_unversioned_service_type(self):
        """Return type of service without versions.

        Some services are versioned like volumev2 and volumev3, we try to
        discover these services checking the supported versions, so we need
        to know the unversioned service type for this.
        The default value is the type of the service.
        """
        return self.s_type

    def post_configuration(self, conf, is_service):
        """Do post congiruation steps.

        :param conf: config_tempest.tempest_conf.TempestConf
        :param is_service: config_tempest.services.services.Services.is_service
        """
        return None


class VersionedService(Service):
    def set_versions(self, top_level=True):
        body = self.do_get(self.service_url, top_level=top_level)
        self.versions_body = json.loads(body)
        self.versions = self.deserialize_versions(self.versions_body)

    def deserialize_versions(self, body):
        versions = []
        for version in body['versions']:
            if version['status'] != "DEPRECATED":
                versions.append(version)
        return list(map(lambda x: x['id'], versions))

    def filter_api_microversions(self):
        min_microversion = ''
        max_microversion = ''
        for version in self.versions_body['versions']:
            if version['status'] != "DEPRECATED":
                if max_microversion == '':
                    max_microversion = version['version']
                else:
                    max_microversion = max(max_microversion,
                                           version['version'])
                if 'min_version' not in version:
                    continue
                if min_microversion == '':
                    min_microversion = version['min_version']
                else:
                    min_microversion = min(min_microversion,
                                           version['min_version'])
        return {'max_microversion': max_microversion,
                'min_microversion': min_microversion}

    def no_port_cut_url(self):
        # if there is no port defined, cut the url from version to the end
        u = urllib3.util.parse_url(self.service_url)
        url = self.service_url
        if u.port is None:
            found = re.findall(r'v\d', url)
            if len(found) > 0:
                index = url.index(found[0])
                url = self.service_url[:index]
        return (url, u.port is not None)
