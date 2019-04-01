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

from operator import itemgetter

from config_tempest import constants as C


class Flavors(object):
    def __init__(self, client, allow_creation, conf, min_memory, min_disk,
                 no_rng=False):
        """Init.

        :type client: FlavorsClient object from tempest lib
        :type allow_creation: boolean
        :type conf: TempestConf object
        """
        self.client = client
        self.allow_creation = allow_creation
        self._conf = conf
        self.flavor_list = self.client.list_flavors()['flavors']
        min_memory_alt = C.DEFAULT_FLAVOR_RAM_ALT
        name = 'm1.nano'
        name_alt = 'm1.micro'
        if min_memory != C.DEFAULT_FLAVOR_RAM:
            min_memory_alt = min_memory + 1
            name = 'custom'
            name_alt = 'custom_alt'
        self._conf.set('volume', 'volume_size', str(min_disk))
        self.prefs = [
            {'key': 'flavor_ref', 'name': name, 'ram': min_memory,
             'disk': min_disk, 'no_rng': no_rng},
            {'key': 'flavor_ref_alt', 'name': name_alt,
             'ram': min_memory_alt, 'disk': min_disk, 'no_rng': no_rng}
        ]

    def create_tempest_flavors(self):
        """Find or create flavors and set them in conf.

        If 'flavor_ref' and 'flavor_ref_alt' are specified in conf, it will
        try to find them, if not found, it raises an Exception.
        Otherwise it will try finding or creating the required base flavors
        (m1.nano and m1.micro by default) and set their ids in conf.
        """
        for pref in self.prefs:
            flavor_id = None
            if self._conf.has_option('compute', pref['key']):
                flavor_id = self._conf.get('compute', pref['key'])
                flavor_id = self.find_flavor_by_id(flavor_id)
                if flavor_id is None:
                    raise Exception("%s id '%s' specified by user doesn't"
                                    " exist", pref['key'], flavor_id)
            else:
                flavor_id = self.create_flavor(pref['name'], pref['ram'],
                                               C.DEFAULT_FLAVOR_VCPUS,
                                               pref['disk'],
                                               no_rng=pref['no_rng'])
                self._conf.set('compute', pref['key'], flavor_id)

    def create_flavor(self, flavor_name, ram, vcpus, disk, no_rng=False):
        """Create flavors or try to discover two smallest ones available.

        :param flavor_name: flavor name to be created (usually m1.nano or
                            m1.micro)
        :param ram: memory of created flavor in MB
        :param vcpus: number of VCPUs for the flavor
        :param disk: size of disk for flavor in GB
        :param no_rng: boolean, if True, flavor will be created with RNG device
        """
        flavor_id = self.find_flavor_by_name(flavor_name)
        if flavor_id is not None:
            C.LOG.info("(no change) Found flavor '%s'", flavor_name)
            return flavor_id
        elif self.allow_creation:
            C.LOG.info("Creating flavor '%s'", flavor_name)
            resp = self.client.create_flavor(name=flavor_name,
                                             ram=ram, vcpus=vcpus,
                                             disk=disk, id=None)
            args = {'flavor_id': resp['flavor']['id'],
                    'hw_rng:allowed': 'True'}
            if no_rng:
                args.pop('hw_rng:allowed')
            self.client.set_flavor_extra_spec(**args)
            return resp['flavor']['id']
        else:
            if len(self.flavor_list) < 2:
                raise Exception("Creation of flavors is not allowed and not "
                                "enough available flavors found. Either use --"
                                "create argument or create flavors manually.")
            # return id of the discovered flavor
            return self.discover_smallest_flavor(flavor_name)

    def find_flavor_by_id(self, flavor_id):
        """Look for a flavor by its id.

        :type flavor_id: string
        :return: flavor id or None if not found
        :rtype: string or None
        """
        found = [f for f in self.flavor_list if f['id'] == flavor_id]
        if found:
            C.LOG.info("Found flavor '%s' by it's id '%s'",
                       found[0]['name'], flavor_id)
            # return flavor's id
            return found[0]['id']
        return None

    def find_flavor_by_name(self, flavor_name):
        """Look for a flavor by its name.

        :type flavor_name: string
        :return: flavor id or None if not found
        :rtype: string or None
        """
        found = [f for f in self.flavor_list if f['name'] == flavor_name]
        if found:
            # return flavor's id
            return found[0]['id']
        return None

    def discover_smallest_flavor(self, flavor_name=""):
        """Discover the two smallest available flavors in the system.

        If flavor_name contains "micro", the method returns the second
        smallest flavor found.
        :param flavor_name: [m1.nano, m1.micro]
        """
        C.LOG.warning("Flavor '%s' not found and creation is not allowed. "
                      "Trying to autodetect the smallest flavor available.",
                      flavor_name)
        flavors = []
        for flavor in self.flavor_list:
            f = self.client.show_flavor(flavor['id'])['flavor']
            flavors.append((f['name'], f['id'], f['ram'],
                            f['disk'], f['vcpus']))

        # order by ram, disk size and vcpus number and take first two of them
        flavors = sorted(flavors, key=itemgetter(2, 3, 4))[:2]

        f = None
        if "micro" in flavor_name:
            # take the second smaller one
            f = flavors[1]
        else:
            f = flavors[0]
        C.LOG.warning("Found '%s' flavor (id: '%s', ram: '%s', disk: '%s', "
                      "vcpus: '%s') ", f[0], f[1], f[2], f[3], f[4])
        # return flavor's id
        return f[1]
