# -*- coding: utf-8 -*-

# Copyright 2017 Red Hat, Inc.
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

from config_tempest import config_tempest as tool
from config_tempest.tests.base import BaseConfigTempestTest
from fixtures import MonkeyPatch
import mock


class TestCreateTempestImages(BaseConfigTempestTest):

    def setUp(self):
        super(TestCreateTempestImages, self).setUp()
        self.conf = self._get_conf("v2.0", "v3")
        self.client = self._get_clients(self.conf).images
        self.image_path = "my_path"
        self.allow_creation = False
        self.disk_format = ".format"
        self.dir = "/img/"
        self.conf.set("scenario", "img_dir", self.dir)

    @mock.patch('config_tempest.config_tempest.find_or_upload_image')
    def test_create_tempest_images_exception(self, mock_find_upload):
        mock_find_upload.side_effect = Exception
        exc = Exception
        self.assertRaises(exc,
                          tool.create_tempest_images,
                          client=self.client,
                          conf=self.conf,
                          image_path=self.image_path,
                          allow_creation=self.allow_creation,
                          disk_format=self.disk_format)

    @mock.patch('config_tempest.config_tempest.find_or_upload_image')
    def _test_create_tempest_images(self, mock_find_upload):
        mock_find_upload.side_effect = ["id_c", "id_d"]
        tool.create_tempest_images(client=self.client,
                                   conf=self.conf,
                                   image_path=self.image_path,
                                   allow_creation=self.allow_creation,
                                   disk_format=self.disk_format)
        self.assertEqual(self.conf.get('compute', 'image_ref'), 'id_c')
        self.assertEqual(self.conf.get('compute', 'image_ref_alt'), 'id_d')

    def test_create_tempest_images_ref_alt_ref(self):
        self.conf.set('compute', 'image_ref', 'id_a')
        self.conf.set('compute', 'image_ref_alt', 'id_b')
        self._test_create_tempest_images()

    def test_create_tempest_images_ref_no_alt_ref(self):
        self.conf.set('compute', 'image_ref', 'id_a')
        self._test_create_tempest_images()

    def test_create_tempest_images_no_ref_alt_ref(self):
        self.conf.set('compute', 'image_ref_alt', 'id_b')
        self._test_create_tempest_images()

    def test_create_tempest_images_no_ref_no_alt_ref(self):
        self._test_create_tempest_images()


class TestFindImage(BaseConfigTempestTest):

    CLIENT_MOCK = 'tempest.lib.services.image.v2.images_client.ImagesClient'
    IMAGES_LIST = [
        {"status": "active", "name": "ImageName"},
        {"status": "default", "name": "MyImage"},
        {"status": "active", "name": "MyImage"}
    ]

    def setUp(self):
        super(TestFindImage, self).setUp()
        conf = self._get_conf("v2.0", "v3")
        self.client = self._get_clients(conf).images

    def _mock_list_images(self, return_value, image_name, expected_resp):
        mock_function = mock.Mock(return_value=return_value)
        func2mock = self.CLIENT_MOCK + '.list_images'
        self.useFixture(MonkeyPatch(func2mock, mock_function))
        resp = tool._find_image(client=self.client,
                                image_id=None,
                                image_name=image_name)
        self.assertEqual(resp, expected_resp)

    def test_find_image_found(self):
        expected_resp = {"status": "default", "name": "MyImage"}
        self._mock_list_images(return_value={"images": self.IMAGES_LIST},
                               image_name="MyImage",
                               expected_resp=expected_resp)

    def test_find_image_not_found(self):
        self._mock_list_images(return_value={"images": self.IMAGES_LIST},
                               image_name="DoesNotExist",
                               expected_resp=None)

    def test_find_image_by_id(self):
        expected_resp = {"id": "001", "status": "active", "name": "ImageName"}
        mock_function = mock.Mock(return_value=expected_resp)
        func2mock = self.CLIENT_MOCK + '.show_image'
        self.useFixture(MonkeyPatch(func2mock, mock_function))
        resp = tool._find_image(client=self.client,
                                image_id="001",
                                image_name="cirros")
        self.assertEqual(resp, expected_resp)


class TestFindOrUploadImage(BaseConfigTempestTest):

    def setUp(self):
        super(TestFindOrUploadImage, self).setUp()
        conf = self._get_conf("v2.0", "v3")
        self.client = self._get_clients(conf).images

    @mock.patch('config_tempest.config_tempest._find_image')
    def test_find_or_upload_image_not_found_creation_not_allowed(
            self, mock_find_image):
        mock_find_image.return_value = None
        exc = Exception
        self.assertRaises(exc, tool.find_or_upload_image, client=self.client,
                          image_id=None, image_name=None,
                          allow_creation=False)

    @mock.patch('config_tempest.config_tempest._find_image')
    @mock.patch('config_tempest.config_tempest._download_file')
    @mock.patch('config_tempest.config_tempest._upload_image')
    def _test_find_or_upload_image_not_found_creation_allowed_format(
            self, mock_upload_image,
            mock_download_file, mock_find_image, format):
        mock_find_image.return_value = None
        mock_upload_image.return_value = {"id": "my_fake_id"}
        image_source = format + "://any_random_url"
        image_dest = "my_dest"
        image_name = "my_image"
        disk_format = "my_format"
        image_id = tool.find_or_upload_image(
            client=self.client, image_id=None, image_dest=image_dest,
            image_name=image_name, image_source=image_source,
            allow_creation=True, disk_format=disk_format)
        mock_download_file.assert_called_with(image_source, image_dest)
        mock_upload_image.assert_called_with(self.client,
                                             image_name, image_dest,
                                             disk_format)
        self.assertEqual(image_id, "my_fake_id")

    def test_find_or_upload_image_not_found_creation_allowed_http(self):
        self._test_find_or_upload_image_not_found_creation_allowed_format(
            format="http")

    def test_find_or_upload_image_not_found_creation_allowed_https(self):
        self._test_find_or_upload_image_not_found_creation_allowed_format(
            format="https")

    @mock.patch('shutil.copyfile')
    @mock.patch('config_tempest.config_tempest._find_image')
    @mock.patch('config_tempest.config_tempest._download_file')
    @mock.patch('config_tempest.config_tempest._upload_image')
    def test_find_or_upload_image_not_found_creation_allowed_ftp_old(
            self, mock_upload_image, mock_download_file, mock_find_image,
            mock_copy):
        mock_find_image.return_value = None
        mock_upload_image.return_value = {"id": "my_fake_id"}
        # image source does not start with http or https
        image_source = "ftp://any_random_url"
        image_dest = "place_on_disk"
        disk_format = "my_format"
        image_name = "my_image"
        image_id = tool.find_or_upload_image(
            client=self.client, image_id=None, image_name=image_name,
            image_source=image_source, image_dest=image_dest,
            allow_creation=True, disk_format=disk_format)
        mock_copy.assert_called_with(image_source, image_dest)
        mock_upload_image.assert_called_with(
            self.client, image_name, image_dest, disk_format)
        self.assertEqual(image_id, "my_fake_id")

    @mock.patch('os.path.isfile')
    @mock.patch('config_tempest.config_tempest._find_image')
    def test_find_or_upload_image_found_downloaded(
            self, mock_find_image, mock_isfile):
        mock_find_image.return_value = \
            {"status": "active", "name": "ImageName", "id": "my_fake_id"}
        mock_isfile.return_value = True
        image_id = tool.find_or_upload_image(
            client=self.client, image_id=None,
            image_name=None, allow_creation=True)
        self.assertEqual(image_id, "my_fake_id")

    @mock.patch('config_tempest.config_tempest._download_image')
    @mock.patch('os.path.isfile')
    @mock.patch('config_tempest.config_tempest._find_image')
    def test_find_or_upload_image_found_not_downloaded(
            self, mock_find_image, mock_isfile, mock_download_image):
        image_id = "my_fake_id"
        mock_find_image.return_value = \
            {"status": "active", "name": "ImageName", "id": image_id}
        mock_isfile.return_value = False
        image_id = tool.find_or_upload_image(
            client=self.client, image_id=None,
            image_name=None, allow_creation=True)
        mock_download_image.assert_called()
        self.assertEqual(image_id, "my_fake_id")
