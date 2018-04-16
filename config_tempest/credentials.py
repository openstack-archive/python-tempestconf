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

from tempest.lib import auth


class Credentials(object):
    """Class contains all needed credentials.

    Wrapps credentials obtained from TempestConf object and Tempest
    credentialsfrom auth library.
    """
    def __init__(self, conf, admin):
        """Init method of Credentials.

        :type conf: TempestConf object
        :param admin: True if the user is admin, False otherwise
        :type admin: Boolean
        """
        self.admin = admin
        self._conf = conf
        self.username = self.get_credential('username')
        self.password = self.get_credential('password')
        self.tenant_name = self.get_credential('tenant_name')
        self.identity_version = self._get_identity_version()
        self.api_version = 3 if self.identity_version == "v3" else 2
        self.identity_region = self._conf.get_defaulted('identity', 'region')
        self.disable_ssl_certificate_validation = self._conf.get_defaulted(
            'identity',
            'disable_ssl_certificate_validation'
        )
        self.ca_certs = self._conf.get_defaulted('identity',
                                                 'ca_certificates_file')
        self.set_credentials()

    def get_credential(self, key):
        """Helper for getting credential by its name.

        :param key: credential name
        :type key: string
        :returns: credential
        :rtype: string
        """
        admin_prefix = 'admin_' if self.admin else ""
        return self.get_identity_credential(admin_prefix + key)

    def get_identity_credential(self, key):
        """Get credential requested by its name.

        The function is providing the backwards compatibility for looking up
        the credentials, because admin credentials were moved from identity
        to auth section and admin_tenant_name was renamed to
        admin_project_name.
        :param key: name of the credential e.g. username, passsword ...
        :type key: string
        :returns: credential
        :rtype: string
        """
        if key == 'admin_tenant_name':
            value = self._conf.get_defaulted('auth', 'admin_project_name')
        else:
            value = self._conf.get_defaulted('auth', key)
        if value is None:
            return self._conf.get_defaulted('identity', key)
        return value

    def _get_identity_version(self):
        """Looks for identity version in TempestConf object.

        :returns: identity version
        :rtype: string
        """
        if "v3" in self._conf.get("identity", "uri"):
            return "v3"
        else:
            return "v2"

    def _get_creds_kwargs(self):
        """Creates kwargs.

        Kwargs based on the identity version, for obtaining
        Tempest credentials.

        :returns: kwargs
        :rtype: dict
        """
        creds_kwargs = {'username': self.username,
                        'password': self.password}
        if self.identity_version == 'v3':
            creds_kwargs.update({'project_name': self.tenant_name,
                                 'domain_name': 'Default',
                                 'user_domain_name': 'Default'})
        else:
            creds_kwargs.update({'tenant_name': self.tenant_name})
        return creds_kwargs

    def set_credentials(self):
        """Gets and saves Tempest credentials from auth library."""
        creds_kwargs = self._get_creds_kwargs()
        disable_ssl = self.disable_ssl_certificate_validation
        self.tempest_creds = auth.get_credentials(
            auth_url=None,
            fill_in=False,
            identity_version=self.identity_version,
            disable_ssl_certificate_validation=disable_ssl,
            ca_certs=self.ca_certs,
            **creds_kwargs)

    def get_auth_provider(self):
        """Gets auth provider based on the type of Tempest credentials.

        :returns: auth provider
        :rtype: auth.KeystoneV2AuthProvider/auth.KeystoneV3AuthProvider
        """
        if isinstance(self.tempest_creds, auth.KeystoneV3Credentials):
            return auth.KeystoneV3AuthProvider(
                self.tempest_creds,
                self._conf.get_defaulted('identity', 'uri_v3'),
                self.disable_ssl_certificate_validation,
                self.ca_certs)
        else:
            return auth.KeystoneV2AuthProvider(
                self.tempest_creds,
                self._conf.get_defaulted('identity', 'uri'),
                self.disable_ssl_certificate_validation,
                self.ca_certs)
