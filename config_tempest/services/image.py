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

import os
import shutil
import urllib2

from base import VersionedService
from config_tempest.constants import LOG
from tempest.lib import exceptions


class ImageService(VersionedService):

    def __init__(self, name, service_url, token, disable_ssl_validation,
                 client=None):
        super(ImageService, self).__init__(name, service_url, token,
                                           disable_ssl_validation,
                                           client)
        self.allow_creation = False
        self.image_path = ""
        self.disk_format = ""

    def set_image_preferences(self, allow_creation, image_path, disk_format):
        """Sets image prefferences.

        :type allow_creation: boolean
        :type image_path: string
        :type disk_format: string
        """
        self.allow_creation = allow_creation
        self.image_path = image_path
        self.disk_format = disk_format

    def set_versions(self):
        super(ImageService, self).set_versions(top_level=False)

    def create_tempest_images(self, conf):
        """Uploads an image to the glance.

        The method creates images specified in conf, if they're not created
        already. Then it sets their IDs to the conf.

        :type conf: TempestConf object
        """
        img_path = os.path.join(conf.get("scenario", "img_dir"),
                                os.path.basename(self.image_path))
        name = self.image_path[self.image_path.rfind('/') + 1:]
        conf.set('scenario', 'img_file', name)
        alt_name = name + "_alt"
        image_id = None
        if conf.has_option('compute', 'image_ref'):
            image_id = conf.get('compute', 'image_ref')
        image_id = self.find_or_upload_image(image_id, name,
                                             image_source=self.image_path,
                                             image_dest=img_path)
        alt_image_id = None
        if conf.has_option('compute', 'image_ref_alt'):
            alt_image_id = conf.get('compute', 'image_ref_alt')
        alt_image_id = self.find_or_upload_image(alt_image_id, alt_name,
                                                 image_source=self.image_path,
                                                 image_dest=img_path)

        conf.set('compute', 'image_ref', image_id)
        conf.set('compute', 'image_ref_alt', alt_image_id)

    def find_or_upload_image(self, image_id, image_name, image_source='',
                             image_dest=''):
        """If the image is not found, uploads it.

        :type image_id: string
        :type image_name: string
        :type image_source: string
        :type image_dest: string
        """
        image = self._find_image(image_id, image_name)
        if not image and not self.allow_creation:
            raise Exception("Image '%s' not found, but resource creation"
                            " isn't allowed. Either use '--create' or provide"
                            " an existing image_ref" % image_name)

        if image:
            LOG.info("(no change) Found image '%s'", image['name'])
            path = os.path.abspath(image_dest)
            if not os.path.isfile(path):
                self._download_image(image['id'], path)
        else:
            LOG.info("Creating image '%s'", image_name)
            if image_source.startswith("http:") or \
               image_source.startswith("https:"):
                    self._download_file(image_source, image_dest)
            else:
                shutil.copyfile(image_source, image_dest)
            image = self._upload_image(image_name, image_dest)
        return image['id']

    def _find_image(self, image_id, image_name):
        """Find image by ID or name (the image client doesn't have this).

        :type image_id: string
        :type image_name: string
        """
        if image_id:
            try:
                return self.client.show_image(image_id)
            except exceptions.NotFound:
                pass
        found = filter(lambda x: x['name'] == image_name,
                       self.client.list_images()['images'])
        if found:
            return found[0]
        else:
            return None

    def _upload_image(self, name, path):
        """Upload image file from `path` into Glance with `name`.

        :type name: string
        :type path: string
        """
        LOG.info("Uploading image '%s' from '%s'", name, os.path.abspath(path))

        with open(path) as data:
            image = self.client.create_image(name=name,
                                             disk_format=self.disk_format,
                                             container_format='bare',
                                             visibility="public")
            self.client.store_image_file(image['id'], data)
            return image

    def _download_image(self, id, path):
        """Download image from glance.

        :type id: string
        :type path: string
        """
        LOG.info("Downloading image %s to %s", id, path)
        body = self.client.show_image_file(id)
        LOG.debug(type(body.data))
        with open(path, 'wb') as out:
            out.write(body.data)

    def _download_file(self, url, destination):
        """Downloads a file specified by `url` to `destination`.

        :type url: string
        :type destination: string
        """
        if os.path.exists(destination):
            LOG.info("Image '%s' already fetched to '%s'.", url, destination)
            return
        LOG.info("Downloading '%s' and saving as '%s'", url, destination)
        f = urllib2.urlopen(url)
        data = f.read()
        with open(destination, "wb") as dest:
            dest.write(data)
