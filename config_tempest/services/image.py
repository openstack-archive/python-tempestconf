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

from six.moves import urllib
from tempest.lib import exceptions

from config_tempest import constants as C
from config_tempest.services.base import VersionedService


class ImageService(VersionedService):

    def __init__(self, name, service_url, token, disable_ssl_validation,
                 client=None):
        super(ImageService, self).__init__(name, service_url, token,
                                           disable_ssl_validation,
                                           client)

    def set_image_preferences(self, disk_format, non_admin):
        """Sets image prefferences.

        :type disk_format: string
        :type non_admin: bool
        """
        self.disk_format = disk_format
        self.non_admin = non_admin

    def set_default_tempest_options(self, conf):
        # When cirros is the image, set validation.image_ssh_user to cirros.
        # The option is heavily used in CI and it's also usefull for refstack,
        # because we don't have to specify overrides.
        if 'cirros' in conf.get_defaulted('image',
                                          'image_path').rsplit('/')[-1]:
            conf.set('validation', 'image_ssh_user', 'cirros')
        # image.http_image is a tempest option which defines 'http accessible
        # image', it can be in a compressed format so it can't be mistaken
        # for an image which will be uploaded to the glance.
        # image.http_image and image.image_path can be 2 different images.
        # If image.http_image wasn't set as an override, it will be set to
        # image.image_path or to DEFAULT_IMAGE
        image_path = conf.get_defaulted('image', 'image_path')
        if self._find_image_by_name(image_path) is None:
            conf.set('image', 'http_image', image_path)
        else:
            # image.image_path is name of the image already present in glance,
            # this value can't be set to image.http_image, therefor set the
            # default value
            conf.set('image', 'http_image', C.DEFAULT_IMAGE)

    def get_supported_versions(self):
        return ['v1', 'v2']

    @staticmethod
    def get_service_name():
        return ['glance']

    def get_catalog(self):
        return 'image'

    def set_versions(self):
        super(ImageService, self).set_versions(top_level=False)

    def create_tempest_images(self, conf):
        """Uploads an image to the glance.

        The method creates images specified in conf, if they're not created
        already. Then it sets their IDs to the conf.

        :type conf: TempestConf object
        """
        img_dir = os.path.join(conf.get("scenario", "img_dir"))
        image_path = conf.get_defaulted('image', 'image_path')
        img_path = os.path.join(img_dir,
                                os.path.basename(image_path))
        name = image_path[image_path.rfind('/') + 1:]
        if not os.path.exists(img_dir):
            try:
                os.makedirs(img_dir)
            except OSError:
                raise
        conf.set('scenario', 'img_file', name)
        alt_name = name + "_alt"
        image_id = None
        if conf.has_option('compute', 'image_ref'):
            image_id = conf.get('compute', 'image_ref')
        image_id = self.find_or_upload_image(image_id, name,
                                             image_source=image_path,
                                             image_dest=img_path)
        alt_image_id = None
        if conf.has_option('compute', 'image_ref_alt'):
            alt_image_id = conf.get('compute', 'image_ref_alt')
        alt_image_id = self.find_or_upload_image(alt_image_id, alt_name,
                                                 image_source=image_path,
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

        if image:
            C.LOG.info("(no change) Found image '%s'", image['name'])
            path = os.path.abspath(image_dest)
            if not os.path.isfile(path):
                self._download_image(image['id'], path)
        else:
            C.LOG.info("Creating image '%s'", image_name)
            if image_source.startswith("http:") or \
               image_source.startswith("https:"):
                    self._download_file(image_source, image_dest)
            else:
                try:
                    shutil.copyfile(image_source, image_dest)
                except IOError:
                    # let's try if this is the case when a user uses already
                    # existing image in glance which is not uploaded as *_alt
                    if image_name[-4:] == "_alt":
                        image = self._find_image(None, image_name[:-4])
                        if image:
                            path = os.path.abspath(image_dest)
                            if not os.path.isfile(path):
                                self._download_image(image['id'], path)
                    else:
                        raise IOError
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
        return self._find_image_by_name(image_name)

    def _find_image_by_name(self, image_name):
        """Find image by name.

        :type image_name: string
        :return: Information in a dict about the found image
        :rtype: dict or None if image was not found
        """
        for x in self.client.list_images()['images']:
            if x['name'] == image_name:
                return x
        return None

    def _upload_image(self, name, path):
        """Upload image file from `path` into Glance with `name`.

        :type name: string
        :type path: string
        """
        C.LOG.info("Uploading image '%s' from '%s'",
                   name, os.path.abspath(path))
        if self.non_admin:
            visibility = 'community'
        else:
            visibility = 'public'

        with open(path, 'rb') as data:
            image = self.client.create_image(name=name,
                                             disk_format=self.disk_format,
                                             container_format='bare',
                                             visibility=visibility)
            self.client.store_image_file(image['id'], data)
        return image

    def _download_image(self, id, path):
        """Download image from glance.

        :type id: string
        :type path: string
        """
        C.LOG.info("Downloading image %s to %s", id, path)
        body = self.client.show_image_file(id)
        C.LOG.debug(type(body.data))
        with open(path, 'wb') as out:
            out.write(body.data)

    def _download_file(self, url, destination):
        """Downloads a file specified by `url` to `destination`.

        :type url: string
        :type destination: string
        """
        if os.path.exists(destination):
            C.LOG.info("Image '%s' already fetched to '%s'.", url, destination)
            return
        C.LOG.info("Downloading '%s' and saving as '%s'", url, destination)
        f = urllib.request.urlopen(url)
        data = f.read()
        with open(destination, "wb") as dest:
            dest.write(data)
