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


from ssl import CertificateError

from six.moves import urllib

from config_tempest import constants as C


def configure_horizon(conf):
    """Derive the horizon URIs from the identity's URI."""
    uri = conf.get('identity', 'uri')
    u = urllib.parse.urlparse(uri)
    base = '%s://%s%s' % (u.scheme, u.netloc.replace(
        ':' + str(u.port), ''), '/dashboard')
    assert base.startswith('http:') or base.startswith('https:')
    has_horizon = True
    try:
        urllib.request.urlopen(base)
    except urllib.error.URLError:
        has_horizon = False
    except CertificateError as ex:
        C.LOG.info('Certificate Error while discovering Horizon: %s', (ex))
        has_horizon = False

    conf.set('service_available', 'horizon', str(has_horizon))
    if has_horizon:
        conf.set('dashboard', 'dashboard_url', base + '/')
        conf.set('dashboard', 'login_url', base + '/auth/login/')
