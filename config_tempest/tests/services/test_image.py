# Copyright 2018 Red Hat, Inc.
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

from unittest import mock

from fixtures import MonkeyPatch

from config_tempest.services.image import ImageService
from config_tempest.tempest_conf import TempestConf
from config_tempest.tests.base import BaseServiceTest


class TestImageService(BaseServiceTest):

    CLIENT_MOCK = 'tempest.lib.services.image.v2.images_client.ImagesClient'
    IMAGES_LIST = [
        {"status": "active", "name": "ImageName"},
        {"status": "default", "name": "MyImage"},
        {"status": "active", "name": "MyImage"}
    ]

    def setUp(self):
        super(TestImageService, self).setUp()
        self.Service = ImageService("ServiceName",
                                    "ServiceType",
                                    self.FAKE_URL,
                                    self.FAKE_TOKEN,
                                    disable_ssl_validation=False)
        self.Service.disk_format = ".format"
        self.Service.non_admin = False
        self.Service.convert = False
        self.Service.client = self.FakeServiceClient()

        self.dir = "/img/"
        self.conf = TempestConf()
        self.conf.set("scenario", "img_dir", self.dir)
        self.conf.set("image", "image_path", "my_image.qcow2")
        self.conf.set("image", "http_image", "http_image.qcow2")

    @mock.patch('config_tempest.services.image.ImageService._find_image')
    @mock.patch('config_tempest.services.image.ImageService'
                '.find_or_upload_image')
    @mock.patch('os.makedirs')
    def _test_create_tempest_images(self, mock_makedirs, mock_find_upload,
                                    mock_find_image):
        mock_find_upload.side_effect = ["id_c", "id_d"]
        mock_find_image.return_value = {'name': 'my_image.qcow2'}
        self.Service.create_tempest_images(conf=self.conf)
        mock_makedirs.assert_called()
        self.assertEqual(self.conf.get('compute', 'image_ref'), 'id_c')
        self.assertEqual(self.conf.get('compute', 'image_ref_alt'), 'id_d')
        self.assertEqual(self.conf.get('scenario', 'img_file'),
                         'my_image.qcow2')

    @mock.patch('config_tempest.services.image.ImageService._find_image')
    @mock.patch('config_tempest.services.image.ImageService._download_file')
    @mock.patch('config_tempest.services.image.ImageService._upload_image')
    def _test_find_or_upload_image_not_found_creation_allowed_format(
            self, mock_upload_image,
            mock_download_file, mock_find_image, format):
        mock_find_image.return_value = None
        mock_upload_image.return_value = {"id": "my_fake_id"}
        image_source = format + "://any_random_url"
        image_dest = "my_dest"
        image_name = "my_image"
        image_id = self.Service.find_or_upload_image(
            image_id=None, image_dest=image_dest,
            image_name=image_name, image_source=image_source)
        mock_download_file.assert_called_with(image_source, image_dest)
        mock_upload_image.assert_called_with(image_name, image_dest)
        self.assertEqual(image_id, "my_fake_id")

    def _mock_list_images(self, return_value, image_name, expected_resp):

        mock_function = mock.Mock(return_value=return_value)
        func2mock = self.FAKE_CLIENT_MOCK + '.list_images'
        self.useFixture(MonkeyPatch(func2mock, mock_function))
        resp = self.Service._find_image(image_id=None,
                                        image_name=image_name)
        self.assertEqual(resp, expected_resp)

    def test_set_get_versions(self):
        exp_resp = ['v2.0', 'v2.1']
        self._set_get_versions(self.Service, exp_resp, self.FAKE_VERSIONS)

    @mock.patch('config_tempest.services.image.ImageService'
                '.find_or_upload_image')
    def test_create_tempest_images_exception(self, mock_find_upload):
        mock_find_upload.side_effect = Exception
        exc = Exception
        self.assertRaises(exc,
                          self.Service.create_tempest_images,
                          conf=self.conf)

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

    @mock.patch('config_tempest.services.image.ImageService._find_image')
    def test_find_or_upload_image_not_found_creation_not_allowed(
            self, mock_find_image):
        mock_find_image.return_value = None
        exc = Exception
        self.assertRaises(exc, self.Service.find_or_upload_image,
                          image_id=None, image_name=None)

    def test_find_or_upload_image_not_found_creation_allowed_http(self):
        self._test_find_or_upload_image_not_found_creation_allowed_format(
            format="http")

    def test_find_or_upload_image_not_found_creation_allowed_https(self):
        self._test_find_or_upload_image_not_found_creation_allowed_format(
            format="https")

    @mock.patch('shutil.copyfile')
    @mock.patch('config_tempest.services.image.ImageService._find_image')
    @mock.patch('config_tempest.services.image.ImageService._download_file')
    @mock.patch('config_tempest.services.image.ImageService._upload_image')
    def test_find_or_upload_image_not_found_creation_allowed_ftp_old(
            self, mock_upload_image, mock_download_file, mock_find_image,
            mock_copy):
        mock_find_image.return_value = None
        mock_upload_image.return_value = {"id": "my_fake_id"}
        # image source does not start with http or https
        image_source = "ftp://any_random_url"
        image_dest = "place_on_disk"
        image_name = "my_image"
        image_id = self.Service.find_or_upload_image(
            image_id=None, image_name=image_name,
            image_source=image_source, image_dest=image_dest)
        mock_copy.assert_called_with(image_source, image_dest)
        mock_upload_image.assert_called_with(
            image_name, image_dest)
        self.assertEqual(image_id, "my_fake_id")

    @mock.patch('os.path.isfile')
    @mock.patch('config_tempest.services.image.ImageService._find_image')
    def test_find_or_upload_image_found_downloaded(
            self, mock_find_image, mock_isfile):
        mock_find_image.return_value = \
            {"status": "active", "name": "ImageName", "id": "my_fake_id"}
        mock_isfile.return_value = True
        image_id = self.Service.find_or_upload_image(
            image_id=None, image_name=None)
        self.assertEqual(image_id, "my_fake_id")

    @mock.patch('config_tempest.services.image.ImageService._download_image')
    @mock.patch('os.path.isfile')
    @mock.patch('config_tempest.services.image.ImageService._find_image')
    def test_find_or_upload_image_found_not_downloaded(
            self, mock_find_image, mock_isfile, mock_download_image):
        image_id = "my_fake_id"
        mock_find_image.return_value = \
            {"status": "active", "name": "ImageName", "id": image_id}
        mock_isfile.return_value = False
        image_id = self.Service.find_or_upload_image(
            image_id=None, image_name=None)
        mock_download_image.assert_called()
        self.assertEqual(image_id, "my_fake_id")

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
        func2mock = self.FAKE_CLIENT_MOCK + '.show_image'
        self.useFixture(MonkeyPatch(func2mock, mock_function))
        resp = self.Service._find_image(image_id="001",
                                        image_name="cirros")
        self.assertEqual(resp, expected_resp)

    @mock.patch('subprocess.call')
    @mock.patch('os.path.exists')
    def test_convert_image_to_raw(self, mock_exists, mock_subcall):
        path = '/path/of/my/image.qcow2'
        raw_path = '/path/of/my/image.raw'
        mock_exists.return_value = False
        mock_subcall.return_value = 0
        self.Service.convert_image_to_raw(path)
        mock_subcall.assert_called_with(['qemu-img', 'convert',
                                        path, raw_path])
        self.assertEqual(self.Service.disk_format, 'raw')
