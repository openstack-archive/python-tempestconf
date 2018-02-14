#!/usr/bin/env python

# Copyright 2013 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
import logging
import re
import requests
import urllib3
import urlparse

LOG = logging.getLogger(__name__)
MULTIPLE_SLASH = re.compile(r'/+')


class ServiceError(Exception):
    pass


class Service(object):
    def __init__(self, name, service_url, token, disable_ssl_validation):
        self.name = name
        self.service_url = service_url
        self.headers = {'Accept': 'application/json', 'X-Auth-Token': token}
        self.disable_ssl_validation = disable_ssl_validation

    def do_get(self, url, top_level=False, top_level_path=""):
        parts = list(urlparse.urlparse(url))
        # 2 is the path offset
        if top_level:
            parts[2] = '/' + top_level_path

        parts[2] = MULTIPLE_SLASH.sub('/', parts[2])
        url = urlparse.urlunparse(parts)

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

    def get_extensions(self):
        return []

    def get_versions(self):
        return []


class VersionedService(Service):
    def get_versions(self, top_level=True):
        body = self.do_get(self.service_url, top_level=top_level)
        body = json.loads(body)
        return self.deserialize_versions(body)

    def deserialize_versions(self, body):
        return map(lambda x: x['id'], body['versions'])

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


class ComputeService(VersionedService):
    def get_extensions(self):
        body = self.do_get(self.service_url + '/extensions')
        body = json.loads(body)
        return map(lambda x: x['alias'], body['extensions'])

    def get_versions(self):
        url, top_level = self.no_port_cut_url()
        body = self.do_get(url, top_level=top_level)
        body = json.loads(body)
        return self.deserialize_versions(body)


class ImageService(VersionedService):
    def get_versions(self):
        return super(ImageService, self).get_versions(top_level=False)


class NetworkService(VersionedService):
    def get_extensions(self):
        body = self.do_get(self.service_url + '/v2.0/extensions.json')
        body = json.loads(body)
        return map(lambda x: x['alias'], body['extensions'])


class VolumeService(VersionedService):
    def get_extensions(self):
        body = self.do_get(self.service_url + '/extensions')
        body = json.loads(body)
        return map(lambda x: x['alias'], body['extensions'])

    def get_versions(self):
        url, top_level = self.no_port_cut_url()
        body = self.do_get(url, top_level=top_level)
        body = json.loads(body)
        return self.deserialize_versions(body)


class IdentityService(VersionedService):
    def __init__(self, name, service_url, token, disable_ssl_validation):
        super(VersionedService, self).__init__(
            name, service_url, token, disable_ssl_validation)
        version = ''
        if 'v2' in self.service_url:
            version = '/v2.0'
            url_parse = urlparse.urlparse(self.service_url)
            self.service_url = '{}://{}{}'.format(url_parse.scheme,
                                                  url_parse.netloc, version)

    def get_extensions(self):
        if 'v2' in self.service_url:
            body = self.do_get(self.service_url + '/extensions')
            body = json.loads(body)
            return map(lambda x: x['alias'], body['extensions']['values'])
        # Keystone api changed in v3, the concept of extensions change. Right
        # now, all the existin extensions are part of keystone core api, so,
        # there's no longer the /extensions endpoint. The extensions that are
        # stable, are enabled by default, the ones marked as experimental are
        # disabled by default. Checking the tempest source, there's no test
        # pointing to extensions endpoint, so I am very confident that this
        # will not be an issue. If so, we need to list all the /OS-XYZ
        # extensions to identify what is enabled or not. This would be a manual
        # check every time keystone change, add or delete an extension, so I
        # rather prefer to return empty here for now.
        return []

    def deserialize_versions(self, body):
        try:
            versions = []
            for v in body['versions']['values']:
                    # TripleO is in transition to v3 only, so the environment
                    # still returns v2 versions even though they're deprecated.
                    # Therefor pick only versions with stable status.
                if v['status'] == 'stable':
                    versions.append(v['id'])
            return versions
        except KeyError:
            return [body['version']['id']]

    def get_versions(self):
        return super(IdentityService, self).get_versions(top_level=False)


class ObjectStorageService(Service):
    def get_extensions(self):
        body = self.do_get(self.service_url, top_level=True,
                           top_level_path="info")
        body = json.loads(body)
        # Remove Swift general information from extensions list
        body.pop('swift')
        return body.keys()


service_dict = {'compute': ComputeService,
                'image': ImageService,
                'network': NetworkService,
                'object-store': ObjectStorageService,
                'volumev3': VolumeService,
                'identity': IdentityService}


def get_service_class(service_name):
    return service_dict.get(service_name, Service)


def get_identity_v3_extensions(keystone_v3_url):
    """Returns discovered identity v3 extensions

    As keystone V3 uses a JSON Home to store the extensions,
    this method is kept  here just for the sake of functionality, but it
    implements a different discovery method.

    :param keystone_v3_url: Keystone V3 auth url
    :return: A list with the discovered extensions
    """
    try:
        r = requests.get(keystone_v3_url,
                         verify=False,
                         headers={'Accept': 'application/json-home'})
    except requests.exceptions.RequestException as re:
        LOG.error("Request on service '%s' with url '%s' failed",
                  'identity', keystone_v3_url)
        raise re
    ext_h = 'http://docs.openstack.org/api/openstack-identity/3/ext/'
    res = [x for x in json.loads(r.content)['resources'].keys()]
    ext = [ex for ex in res if 'ext' in ex]
    return list(set([str(e).replace(ext_h, '').split('/')[0] for e in ext]))


def discover(auth_provider, region, object_store_discovery=True,
             api_version=2, disable_ssl_certificate_validation=True):
    """Returns a dict with discovered apis.

    :param auth_provider: An AuthProvider to obtain service urls.
    :param region: A specific region to use. If the catalog has only one region
    then that region will be used.
    :return: A dict with an entry for the type of each discovered service.
        Each entry has keys for 'extensions' and 'versions'.
    """
    token, auth_data = auth_provider.get_auth()
    services = {}
    service_catalog = 'serviceCatalog'
    public_url = 'publicURL'
    identity_port = urlparse.urlparse(auth_provider.auth_url).port
    if identity_port is None:
        identity_port = ""
    else:
        identity_port = ":" + str(identity_port)
    identity_version = urlparse.urlparse(auth_provider.auth_url).path
    if api_version == 3:
        service_catalog = 'catalog'
        public_url = 'url'

    # FIXME(chandankumar): It is a workaround to filter services whose
    # endpoints does not exist. Once it is merged. Let's rewrite the whole
    # stuff.
    auth_data[service_catalog] = [data for data in auth_data[service_catalog]
                                  if data['endpoints']]

    for entry in auth_data[service_catalog]:
        name = entry['type']
        services[name] = dict()
        for _ep in entry['endpoints']:
            if api_version == 3:
                if _ep['region'] == region and _ep['interface'] == 'public':
                    ep = _ep
                    break
            else:
                if _ep['region'] == region:
                    ep = _ep
                    break
        else:
            ep = entry['endpoints'][0]
        if 'identity' in ep[public_url]:
            services[name]['url'] = ep[public_url].replace(
                "/identity", "{0}{1}".format(
                    identity_port, identity_version))
        else:
            services[name]['url'] = ep[public_url]
        service_class = get_service_class(name)
        service = service_class(name, services[name]['url'], token,
                                disable_ssl_certificate_validation)
        if name == 'object-store' and not object_store_discovery:
            services[name]['extensions'] = []
        elif 'v3' not in ep[public_url]:  # is not v3 url
            services[name]['extensions'] = service.get_extensions()
        services[name]['versions'] = service.get_versions()
    return services
