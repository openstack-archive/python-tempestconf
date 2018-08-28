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
MULTIPLE_SLASH = re.compile(r'/+')


class ServiceError(Exception):
    pass


class Service(object):
    def __init__(self, name, service_url, token, disable_ssl_validation,
                 client=None):
        self.name = name
        self.service_url = service_url
        self.headers = {'Accept': 'application/json', 'X-Auth-Token': token}
        self.disable_ssl_validation = disable_ssl_validation
        self.client = client

        self.extensions = []
        self.versions = []

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
                      (self.name, url))
            raise e
        if r.status >= 400:
            raise ServiceError("Request on service '%s' with url '%s' failed"
                               " with code %d" % (self.name, url, r.status))
        return r.data

    def set_extensions(self):
        self.extensions = []

    def set_versions(self):
        self.versions = []

    def get_extensions(self):
        return self.extensions

    @staticmethod
    def get_service_name():
        """Return the service name.

        This return a list because you can have different services for the
        same type, like volume, volumev2, volumev3
        """
        return []

    def get_versions(self):
        """Return the versions available for each service.

        This doesn't means tempestconf support all these versions. Only that
        the service have these api versions enabled.
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

    def get_catalog(self):
        """Return the catalog name of a service.

        Usually the catalog has the same name of the service, in some cases
        this is not true, like in volume, that we have volumev3 and volumev2
        for example.
        """
        return self.name

    def get_feature_name(self):
        """Return the name of service used in <service>-feature-enabled.

        Some services have the -feature-enabled option in tempest, that
        diverges from the service name. The main example is object-store
        service where the <service>-feature-enabled is object-storage.
        """
        return self.name

    def get_service_extension_key(self):
        """Return the extension key for a particular service"""
        return None

    def get_unversioned_service_name(self):
        """Return name of service without versions.

        Some services are versioned like volumev2 and volumev3, we try to
        discover these services checking the supported versions, so we need
        to know the unversioned service name for this.
        The default value is the name of the service.
        """
        return self.name


class VersionedService(Service):
    def set_versions(self, top_level=True):
        body = self.do_get(self.service_url, top_level=top_level)
        body = json.loads(body)
        self.versions = self.deserialize_versions(body)

    def deserialize_versions(self, body):
        versions = []
        for version in body['versions']:
            if version['status'] != "DEPRECATED":
                versions.append(version)
        return list(map(lambda x: x['id'], versions))

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
