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

from config_tempest.constants import LOG


class Flavors(object):
    def __init__(self, client, allow_creation, conf):
        """Init.

        :type client: FlavorsClient object from tempest lib
        :type allow_creation: boolean
        :type conf: TempestConf object
        """
        self.client = client
        self.allow_creation = allow_creation
        self._conf = conf

    def create_tempest_flavors(self):
        """Find or create flavors and set them in conf.

        If 'flavor_ref' and 'flavor_ref_alt' are specified in conf, it will
        first try to find those - otherwise it will try finding or creating
        'm1.nano' and 'm1.micro' and overwrite those options in conf.
        """
        # m1.nano flavor
        flavor_id = None
        if self._conf.has_option('compute', 'flavor_ref'):
            flavor_id = self._conf.get('compute', 'flavor_ref')
        flavor_id = self.find_or_create_flavor(flavor_id, 'm1.nano', ram=64)
        self._conf.set('compute', 'flavor_ref', flavor_id)

        # m1.micro flavor
        alt_flavor_id = None
        if self._conf.has_option('compute', 'flavor_ref_alt'):
            alt_flavor_id = self._conf.get('compute', 'flavor_ref_alt')
        alt_flavor_id = self.find_or_create_flavor(alt_flavor_id, 'm1.micro',
                                                   ram=128)
        self._conf.set('compute', 'flavor_ref_alt', alt_flavor_id)

    def find_or_create_flavor(self, flavor_id, flavor_name,
                              ram=64, vcpus=1, disk=0):
        """Try finding flavor by ID or name, create if not found.

        :param flavor_id: first try finding the flavor by this
        :param flavor_name: find by this if it was not found by ID, create new
            flavor with this name if not found at allCLIENT_MOCK
        :param ram: memory of created flavor in MB
        :param vcpus: number of VCPUs for the flavor
        :param disk: size of disk for flavor in GB
        """
        flavor = None
        flavors = self.client.list_flavors()['flavors']
        # try finding it by the ID first
        if flavor_id:
            found = [f for f in flavors if f['id'] == flavor_id]
            if found:
                flavor = found[0]
        # if not found, try finding it by name
        if flavor_name and not flavor:
            found = [f for f in flavors if f['name'] == flavor_name]
            if found:
                flavor = found[0]

        if not flavor and not self.allow_creation:
            raise Exception("Flavor '%s' not found, but resource creation"
                            " isn't allowed. Either use '--create' or provide"
                            " an existing flavor" % flavor_name)

        if not flavor:
            LOG.info("Creating flavor '%s'", flavor_name)
            flavor = self.client.create_flavor(name=flavor_name,
                                               ram=ram, vcpus=vcpus,
                                               disk=disk, id=None)
            return flavor['flavor']['id']
        else:
            LOG.info("(no change) Found flavor '%s'", flavor['name'])

        return flavor['id']
