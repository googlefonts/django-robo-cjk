# -*- coding: utf-8 -*-

from django.conf import settings
from django.test import (
    Client, override_settings, RequestFactory, SimpleTestCase, TestCase,
)
from django.urls import reverse

import fsutil
import json
import requests
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class APIsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.auth_token = None

    def setUp(self):
        # print('setUp')
        pass

    def tearDown(self):
        # print('tearDown')
        pass

    def assert_response_ok(self, response):
        try:
            self.assertEqual(response.status_code, 200)
        except AssertionError as error:
            data = response.json()
            print(data['error'])
            raise error
        data = response.json()
        self.assertEqual(data['status'], 200)
        self.assertEqual(data['error'], None)
        self.assertNotEqual(data['data'], None)
        self.assertTrue(isinstance(data, (dict, list, )))

    def assert_response_error(self, response, expected_status_code):
        self.assertEqual(response.status_code, expected_status_code)
        data = response.json()
        self.assertEqual(data['status'], expected_status_code)
        self.assertNotEqual(data['error'], None)
        self.assertEqual(data['data'], None)

    def assert_response_bad_request(self, response):
        self.assert_response_error(response, 400)

    def assert_response_unauthorized(self, response):
        self.assert_response_error(response, 401)

    def assert_response_forbidden(self, response):
        self.assert_response_error(response, 403)

    def assert_response_not_found(self, response):
        self.assert_response_error(response, 404)

    def assert_response_not_allowed(self, response):
        self.assert_response_error(response, 405)

    def assert_response_internal_server_error(self, response):
        self.assert_response_error(response, 500)

    def assert_response_service_unavailable_error(self, response):
        self.assert_response_error(response, 503)

    @classmethod
    def get_glif_data(cls, path):
        glifpath = fsutil.join_path(__file__, 'test_apis_data', path)
        glifdata = fsutil.read_file(glifpath)
        return glifdata

    @classmethod
    def get_font_uid(cls):
        return 'cbac1f2d-6b6c-46a4-a477-798d49042ff4'

    @classmethod
    def get_response(cls, url, payload=None, files=None, headers=None):
        host = settings.TEST_API_HOST
        # view_url = reverse('view_name')
        absolute_url = '{}{}'.format(host, url)
        payload = payload or {}
        headers = headers or {}
        auth_token = cls.auth_token
        if auth_token is not None:
            headers['Authorization'] = 'Bearer {}'.format(auth_token)
        headers['Cache-Control'] = 'no-cache'
        files = files or []
        options = {
            'data': payload,
            'headers': headers,
            'files': files,
            'verify': False,
        }
        response = requests.post(absolute_url, **options)
        data = response.json()
        return (response, data['data'], )

    def test_0000_auth_token(self):
        # print('test_0000_auth_token')
        payload = {
            'username': settings.TEST_API_USERNAME,
            'password': settings.TEST_API_PASSWORD,
        }
        response, data = self.get_response('/api/auth/token/', payload=payload)
        self.assert_response_ok(response)
        self.assertTrue(isinstance(data, dict))
        auth_token = data['auth_token']
        self.assertTrue(len(auth_token) > 50)
        self.__class__.auth_token = auth_token

    def test_0005_user_list(self):
        # print('test_0005_user_list')
        payload = {
        }
        response, data = self.get_response('/api/user/list/', payload=payload)
        self.assert_response_ok(response)

    def test_0006_user_me(self):
        # print('test_0006_user_me')
        payload = {
        }
        response, data = self.get_response('/api/user/me/', payload=payload)
        self.assert_response_ok(response)

    def test_0010_project_list(self):
        # print('test_0010_project_list')
        payload = {
        }
        response, data = self.get_response('/api/project/list/', payload=payload)
        self.assert_response_ok(response)

    def test_0015_project_get_missing_project_uid(self):
        # print('test_0015_project_get_missing_project_uid')
        payload = {
        }
        response, data = self.get_response('/api/project/get/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0020_project_get(self):
        # print('test_0020_project_get')
        payload = {
            'project_uid': 'fde4fc80-c136-4e2f-a9be-c80e18b9f213',
        }
        response, data = self.get_response('/api/project/get/', payload=payload)
        self.assert_response_ok(response)

    def test_0025_font_list(self):
        # print('test_0025_font_list')
        payload = {
            'project_uid': 'fde4fc80-c136-4e2f-a9be-c80e18b9f213',
        }
        response, data = self.get_response('/api/font/list/', payload=payload)
        self.assert_response_ok(response)

    def test_0030_font_get(self):
        # print('test_0030_font_get')
        payload = {
            'font_uid': self.get_font_uid(),
        }
        response, data = self.get_response('/api/font/get/', payload=payload)
        self.assert_response_ok(response)

    def test_0035_font_update(self):
        # print('test_0035_font_update')
        payload = {
            'font_uid': self.get_font_uid(),
            'fontlib': '{"CJKDesignFrameSettings": {"characterFace": 90, "customsFrames": [], "em_Dimension": [1000, 1000], "horizontalLine": 15, "overshoot": [20, 20], "type": "han", "verticalLine": 15}, "com.typemytype.robofont.guideline.magnetic.bj4ZrgHhis": 5, "com.typemytype.robofont.guideline.showMeasurements.bj4ZrgHhis": false, "com.typemytype.robofont.segmentType": "curve", "robocjk.defaultGlyphWidth": 1000, "robocjk.fontVariations": ["wght"], "robockjk.djangoTest": "ok"}',
        }
        response, data = self.get_response('/api/font/update/', payload=payload)
        self.assert_response_ok(response)

    def test_0040_font_update_revert_change(self):
        # print('test_0040_font_update_revert_change')
        payload = {
            'font_uid': self.get_font_uid(),
            'fontlib': '{"CJKDesignFrameSettings": {"characterFace": 90, "customsFrames": [], "em_Dimension": [1000, 1000], "horizontalLine": 15, "overshoot": [20, 20], "type": "han", "verticalLine": 15}, "com.typemytype.robofont.guideline.magnetic.bj4ZrgHhis": 5, "com.typemytype.robofont.guideline.showMeasurements.bj4ZrgHhis": false, "com.typemytype.robofont.segmentType": "curve", "robocjk.defaultGlyphWidth": 1000, "robocjk.fontVariations": ["wght"]}',
        }
        response, data = self.get_response('/api/font/update/', payload=payload)
        self.assert_response_ok(response)

    def test_0042_glyphs_composition_get(self):
        # print('test_0042_glyphs_composition_get')
        payload = {
            'font_uid': self.get_font_uid(),
        }
        response, data = self.get_response('/api/glyphs-composition/get/', payload=payload)
        self.assert_response_ok(response)

    def test_0043_glyphs_composition_update(self):
        # print('test_0043_glyphs_composition_update')
        payload = {
            'font_uid': self.get_font_uid(),
            'data': '{"Glyphs-Composition-Test":"ok"}',
        }
        response, data = self.get_response('/api/glyphs-composition/update/', payload=payload)
        self.assert_response_ok(response)
        self.assertEqual(data, { 'Glyphs-Composition-Test':'ok' })

    def test_0045_glif_list(self):
        # print('test_0045_glif_list')
        payload = {
            'font_uid': self.get_font_uid(),
        }
        response, data = self.get_response('/api/glif/list/', payload=payload)
        self.assert_response_ok(response)
        self.assertTrue(isinstance(data['atomic_elements'], list))
        self.assertTrue(isinstance(data['deep_components'], list))
        self.assertTrue(isinstance(data['character_glyphs'], list))

    def test_0046_glif_lock(self):
        # print('test_0046_glif_lock')
        payload = {
            'font_uid': self.get_font_uid(),
            'atomic_elements_names': json.dumps(['curvedStroke', 'line']),
            'atomic_elements_ids': 83,
            'deep_components_names': json.dumps(['DC_2008A_00', 'DC_20041_01']),
            'character_glyphs_names': json.dumps(['uni27607']),
        }
        response, data = self.get_response('/api/glif/lock/', payload=payload)
        self.assert_response_ok(response)
        self.assertTrue(isinstance(data['atomic_elements'], list))
        self.assertTrue(isinstance(data['deep_components'], list))
        self.assertTrue(isinstance(data['character_glyphs'], list))
        self.assertEqual(len(data['atomic_elements']), 2)
        self.assertEqual(len(data['deep_components']), 2)
        self.assertEqual(len(data['character_glyphs']), 1)

    def test_0047_glif_unlock(self):
        # print('test_0047_glif_unlock')
        payload = {
            'font_uid': self.get_font_uid(),
            'atomic_elements_names': json.dumps(['curvedStroke', 'line']),
            'atomic_elements_ids': 83,
            'deep_components_names': json.dumps(['DC_2008A_00', 'DC_20041_01']),
            'character_glyphs_names': json.dumps(['uni27607']),
        }
        response, data = self.get_response('/api/glif/unlock/', payload=payload)
        self.assert_response_ok(response)
        self.assertTrue(isinstance(data['atomic_elements'], list))
        self.assertTrue(isinstance(data['deep_components'], list))
        self.assertTrue(isinstance(data['character_glyphs'], list))
        self.assertEqual(len(data['atomic_elements']), 2)
        self.assertEqual(len(data['deep_components']), 2)
        self.assertEqual(len(data['character_glyphs']), 1)

    def test_0050_atomic_element_list(self):
        # print('test_0050_atomic_element_list')
        payload = {
            'font_uid': self.get_font_uid(),
        }
        response, data = self.get_response('/api/atomic-element/list/', payload=payload)
        self.assert_response_ok(response)

    def test_0055_atomic_element_get(self):
        # print('test_0055_atomic_element_get')
        payload = {
            'font_uid': self.get_font_uid(),
            'id': '83',
        }
        response, data = self.get_response('/api/atomic-element/get/', payload=payload)
        self.assert_response_ok(response)

    def test_0060_atomic_element_get_missing_id(self):
        # print('test_0060_atomic_element_get_missing_id')
        payload = {
            'font_uid': self.get_font_uid(),
            # 'id': '83',
        }
        response, data = self.get_response('/api/atomic-element/get/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0065_atomic_element_get_missing_font_uid(self):
        # print('test_0065_atomic_element_get_missing_font_uid')
        payload = {
            # 'font_uid': self.get_font_uid(),
           'id': '83',
        }
        response, data = self.get_response('/api/atomic-element/get/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0070_atomic_element_create(self):
        # print('test_0070_atomic_element_create')
        payload = {
           'font_uid': self.get_font_uid(),
           'data': self.get_glif_data('atomic_element_create/hengpietest.glif'),
        }
        response, data = self.get_response('/api/atomic-element/create/', payload=payload)
        self.assert_response_ok(response)

    def test_0075_atomic_element_lock(self):
        # print('test_0075_atomic_element_lock')
        payload = {
           'font_uid': self.get_font_uid(),
           'name': 'hengpietest',
        }
        response, data = self.get_response('/api/atomic-element/lock/', payload=payload)
        self.assert_response_ok(response)

    def test_0080_atomic_element_update(self):
        # print('test_0080_atomic_element_update')
        payload = {
           'font_uid': self.get_font_uid(),
           'data': self.get_glif_data('atomic_element_update/hengpietest.glif'),
           'name': 'hengpietest',
        }
        response, data = self.get_response('/api/atomic-element/update/', payload=payload)
        self.assert_response_ok(response)

    def test_0085_atomic_element_update_missing_data(self):
        # print('test_0085_atomic_element_update_missing_data')
        payload = {
           'font_uid': self.get_font_uid(),
           # 'data': '',
           'name': 'hengpietest',
        }
        response, data = self.get_response('/api/atomic-element/update/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0090_atomic_element_update_invalid_data(self):
        # print('test_0090_atomic_element_update_invalid_data')
        payload = {
           'font_uid': self.get_font_uid(),
           'data': self.get_glif_data('atomic_element_update_invalid_data/hengpietest.glif'),
           'name': 'hengpietest',
        }
        response, data = self.get_response('/api/atomic-element/update/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0095_atomic_element_update_missing_id(self):
        # print('test_0095_atomic_element_update_missing_id')
        payload = {
           'font_uid': self.get_font_uid(),
           'data': self.get_glif_data('atomic_element_update/hengpietest.glif'),
           # 'name': 'hengpietest',
        }
        response, data = self.get_response('/api/atomic-element/update/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0100_atomic_element_update_status_missing_status(self):
        # print('test_0100_atomic_element_update_status_missing_status')
        payload = {
           'font_uid': self.get_font_uid(),
           'name': 'hengpietest',
        }
        response, data = self.get_response('/api/atomic-element/update-status/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0105_atomic_element_update_status_invalid_status(self):
        # print('test_0105_atomic_element_update_status_invalid_status')
        payload = {
           'font_uid': self.get_font_uid(),
           'name': 'hengpietest',
           'status': 'ok',
        }
        response, data = self.get_response('/api/atomic-element/update-status/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0110_atomic_element_update_status(self):
        # print('test_0110_atomic_element_update_status')
        payload = {
           'font_uid': self.get_font_uid(),
           'name': 'hengpietest',
           'status': 'done',
        }
        response, data = self.get_response('/api/atomic-element/update-status/', payload=payload)
        self.assert_response_ok(response)

    def test_0115_atomic_element_update_status_revert(self):
        # print('test_0115_atomic_element_update_status_revert')
        payload = {
           'font_uid': self.get_font_uid(),
           'name': 'hengpietest',
           'status': 'wip',
        }
        response, data = self.get_response('/api/atomic-element/update-status/', payload=payload)
        self.assert_response_ok(response)

    def test_0120_atomic_element_unlock(self):
        # print('test_0120_atomic_element_unlock')
        payload = {
           'font_uid': self.get_font_uid(),
           'name': 'hengpietest',
        }
        response, data = self.get_response('/api/atomic-element/unlock/', payload=payload)
        self.assert_response_ok(response)

    def test_0125_atomic_element_lock_for_delete(self):
        # print('test_0125_atomic_element_lock_for_delete')
        payload = {
           'font_uid': self.get_font_uid(),
           'name': 'hengpietest',
        }
        response, data = self.get_response('/api/atomic-element/lock/', payload=payload)
        self.assert_response_ok(response)

    def test_0130_atomic_element_delete(self):
        # print('test_0130_atomic_element_delete')
        payload = {
           'font_uid': self.get_font_uid(),
           'name': 'hengpietest',
        }
        response, data = self.get_response('/api/atomic-element/delete/', payload=payload)
        self.assert_response_ok(response)

    def test_0135_atomic_element_lock_for_layer(self):
        # print('test_0135_atomic_element_lock_for_layer')
        payload = {
            'font_uid': self.get_font_uid(),
            'name': 'taperingLineLeft',
        }
        response, data = self.get_response('/api/atomic-element/lock/', payload=payload)
        self.assert_response_ok(response)

    def test_0140_atomic_element_layer_create_integrity_error(self):
        # print('test_0140_atomic_element_layer_create_integrity_error')
        payload = {
            'font_uid': self.get_font_uid(),
            'atomic_element_name': 'taperingLineLeft',
            'data': self.get_glif_data('atomic_element_layer_create_integrity_error/taperingLineLeft.glif'),
        }
        response, data = self.get_response('/api/atomic-element/layer/create/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0145_atomic_element_layer_create(self):
        # print('test_0145_atomic_element_layer_create')
        payload = {
            'font_uid': self.get_font_uid(),
            'atomic_element_name': 'taperingLineLeft',
            'group_name': '4',
            'data': self.get_glif_data('atomic_element_layer_create/taperingLineLeft.glif'),
        }
        response, data = self.get_response('/api/atomic-element/layer/create/', payload=payload)
        self.assert_response_ok(response)

    def test_0150_atomic_element_layer_update(self):
        # print('test_0150_atomic_element_layer_update')
        payload = {
            'font_uid': self.get_font_uid(),
            'atomic_element_name': 'taperingLineLeft',
            'group_name': '4',
            'data': self.get_glif_data('atomic_element_layer_update/taperingLineLeft.glif'),
        }
        response, data = self.get_response('/api/atomic-element/layer/update/', payload=payload)
        self.assert_response_ok(response)

    def test_0155_atomic_element_layer_rename_missing_name(self):
        # print('test_0155_atomic_element_layer_rename_missing_name')
        payload = {
            'font_uid': self.get_font_uid(),
            'atomic_element_name': 'taperingLineLeft',
            'group_name': '4',
        }
        response, data = self.get_response('/api/atomic-element/layer/rename/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0160_atomic_element_layer_rename_existing_name(self):
        # print('test_0160_atomic_element_layer_rename_existing_name')
        payload = {
            'font_uid': self.get_font_uid(),
            'atomic_element_name': 'taperingLineLeft',
            'group_name': '4',
            'new_group_name': '3',
        }
        response, data = self.get_response('/api/atomic-element/layer/rename/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0165_atomic_element_layer_rename(self):
        # print('test_0165_atomic_element_layer_rename')
        payload = {
            'font_uid': self.get_font_uid(),
            'atomic_element_name': 'taperingLineLeft',
            'group_name': '4',
            'new_group_name': '4-renamed',
        }
        response, data = self.get_response('/api/atomic-element/layer/rename/', payload=payload)
        self.assert_response_ok(response)

    def test_0170_atomic_element_layer_rename_revert(self):
        # print('test_0170_atomic_element_layer_rename_revert')
        payload = {
            'font_uid': self.get_font_uid(),
            'atomic_element_name': 'taperingLineLeft',
            'group_name': '4-renamed',
            'new_group_name': '4',
        }
        response, data = self.get_response('/api/atomic-element/layer/rename/', payload=payload)
        self.assert_response_ok(response)

    def test_0175_atomic_element_layer_delete_missing_layer_id_or_layer_name(self):
        # print('test_0175_atomic_element_layer_delete_missing_layer_id_or_layer_name')
        payload = {
            'font_uid': self.get_font_uid(),
            'atomic_element_name': 'taperingLineLeft',
            # 'group_name': '4',
        }
        response, data = self.get_response('/api/atomic-element/layer/delete/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0180_atomic_element_layer_delete(self):
        # print('test_0180_atomic_element_layer_delete')
        payload = {
            'font_uid': self.get_font_uid(),
            'atomic_element_name': 'taperingLineLeft',
            'group_name': '4',
        }
        response, data = self.get_response('/api/atomic-element/layer/delete/', payload=payload)
        self.assert_response_ok(response)

    def test_0185_atomic_element_unlock_for_layer(self):
        # print('test_0185_atomic_element_unlock_for_layer')
        payload = {
            'font_uid': self.get_font_uid(),
            'name': 'taperingLineLeft',
        }
        response, data = self.get_response('/api/atomic-element/unlock/', payload=payload)
        self.assert_response_ok(response)

    def test_0190_deep_component_list(self):
        # print('test_0190_deep_component_list')
        payload = {
            'font_uid': self.get_font_uid(),
        }
        response, data = self.get_response('/api/deep-component/list/', payload=payload)
        self.assert_response_ok(response)

    def test_0195_deep_component_get(self):
        # print('test_0195_deep_component_get')
        payload = {
            'font_uid': self.get_font_uid(),
            'id': 493,
        }
        response, data = self.get_response('/api/deep-component/get/', payload=payload)
        self.assert_response_ok(response)

    def test_0200_deep_component_get_missing_font_id(self):
        # print('test_0200_deep_component_get_missing_font_id')
        payload = {
            # 'font_uid': self.get_font_uid(),
            'id': 493,
        }
        response, data = self.get_response('/api/deep-component/get/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0205_deep_component_get_missing_id(self):
        # print('test_0205_deep_component_get_missing_id')
        payload = {
            'font_uid': self.get_font_uid(),
            # 'id': 493,
        }
        response, data = self.get_response('/api/deep-component/get/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0210_deep_component_create(self):
        # print('test_0210_deep_component_create')
        payload = {
            'font_uid': self.get_font_uid(),
            'data': self.get_glif_data('deep_component_create/DC_200CA_01.glif'),
        }
        response, data = self.get_response('/api/deep-component/create/', payload=payload)
        self.assert_response_ok(response)

    def test_0215_deep_component_lock(self):
        # print('test_0215_deep_component_lock')
        payload = {
            'font_uid': self.get_font_uid(),
            'name': 'DC_200CA_01test',
        }
        response, data = self.get_response('/api/deep-component/lock/', payload=payload)
        self.assert_response_ok(response)

    def test_0220_deep_component_update(self):
        # print('test_0220_deep_component_update')
        payload = {
            'font_uid': self.get_font_uid(),
            'data': self.get_glif_data('deep_component_update/DC_200CA_01.glif'),
            'name': 'DC_200CA_01test',
        }
        response, data = self.get_response('/api/deep-component/update/', payload=payload)
        self.assert_response_ok(response)

    def test_0225_deep_component_update_status(self):
        # print('test_0225_deep_component_update_status')
        payload = {
            'font_uid': self.get_font_uid(),
            'name': 'DC_200CA_01test',
            'status': 'done',
        }
        response, data = self.get_response('/api/deep-component/update-status/', payload=payload)
        self.assert_response_ok(response)

    def test_0230_deep_component_update_status_revert(self):
        # print('test_0230_deep_component_update_status_revert')
        payload = {
            'font_uid': self.get_font_uid(),
            'name': 'DC_200CA_01test',
            'status': 'wip',
        }
        response, data = self.get_response('/api/deep-component/update-status/', payload=payload)
        self.assert_response_ok(response)

    def test_0235_deep_component_unlock(self):
        # print('test_0235_deep_component_unlock')
        payload = {
            'font_uid': self.get_font_uid(),
            'name': 'DC_200CA_01test',
        }
        response, data = self.get_response('/api/deep-component/unlock/', payload=payload)
        self.assert_response_ok(response)

    def test_0240_deep_component_lock_for_delete(self):
        # print('test_0240_deep_component_lock_for_delete')
        payload = {
            'font_uid': self.get_font_uid(),
            'name': 'DC_200CA_01test',
        }
        response, data = self.get_response('/api/deep-component/lock/', payload=payload)
        self.assert_response_ok(response)

    def test_0245_deep_component_delete(self):
        # print('test_0245_deep_component_delete')
        payload = {
            'font_uid': self.get_font_uid(),
            'name': 'DC_200CA_01test',
        }
        response, data = self.get_response('/api/deep-component/delete/', payload=payload)
        self.assert_response_ok(response)

    def test_0250_character_glyph_list(self):
        # print('test_0250_character_glyph_list')
        payload = {
            'font_uid': self.get_font_uid(),
        }
        response, data = self.get_response('/api/character-glyph/list/', payload=payload)
        self.assert_response_ok(response)

    def test_0255_character_glyph_get(self):
        # print('test_0255_character_glyph_get')
        payload = {
            'font_uid': self.get_font_uid(),
            'id': 26281,
        }
        response, data = self.get_response('/api/character-glyph/get/', payload=payload)
        self.assert_response_ok(response)

    def test_0260_character_glyph_get_missing_font_id(self):
        # print('test_0260_character_glyph_get_missing_font_id')
        payload = {
            # 'font_uid': self.get_font_uid(),
            'id': 26281,
        }
        response, data = self.get_response('/api/character-glyph/get/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0265_character_glyph_get_missing_id(self):
        # print('test_0265_character_glyph_get_missing_id')
        payload = {
            'font_uid': self.get_font_uid(),
            # 'id': 26281,
        }
        response, data = self.get_response('/api/character-glyph/get/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0270_character_glyph_create(self):
        # print('test_0270_character_glyph_create')
        payload = {
            'font_uid': self.get_font_uid(),
            'data': self.get_glif_data('character_glyph_create/uni200CA.glif'),
        }
        response, data = self.get_response('/api/character-glyph/create/', payload=payload)
        self.assert_response_ok(response)

    def test_0275_character_glyph_lock(self):
        # print('test_0270_character_glyph_create')
        payload = {
            'font_uid': self.get_font_uid(),
            'name': 'uni200CAtest',
        }
        response, data = self.get_response('/api/character-glyph/lock/', payload=payload)
        self.assert_response_ok(response)

    def test_0280_character_glyph_update(self):
        # print('test_0280_character_glyph_update')
        payload = {
            'font_uid': self.get_font_uid(),
            'name': 'uni200CAtest',
            'data': self.get_glif_data('character_glyph_update/uni200CA.glif'),
        }
        response, data = self.get_response('/api/character-glyph/update/', payload=payload)
        self.assert_response_ok(response)

    def test_0285_character_glyph_update_status(self):
        # print('test_0285_character_glyph_update_status')
        payload = {
            'font_uid': self.get_font_uid(),
            'name': 'uni200CAtest',
            'status': 'checking-1',
        }
        response, data = self.get_response('/api/character-glyph/update-status/', payload=payload)
        self.assert_response_ok(response)

    def test_0285_character_glyph_update_status_revert(self):
        # print('test_0285_character_glyph_update_status_revert')
        payload = {
            'font_uid': self.get_font_uid(),
            'name': 'uni200CAtest',
            'status': 'wip',
        }
        response, data = self.get_response('/api/character-glyph/update-status/', payload=payload)
        self.assert_response_ok(response)

    def test_0290_character_glyph_unlock(self):
        # print('test_0290_character_glyph_unlock')
        payload = {
            'font_uid': self.get_font_uid(),
            'name': 'uni200CAtest',
        }
        response, data = self.get_response('/api/character-glyph/unlock/', payload=payload)
        self.assert_response_ok(response)

    def test_0295_character_glyph_lock_for_delete(self):
        # print('test_0295_character_glyph_lock_for_delete')
        payload = {
            'font_uid': self.get_font_uid(),
            'name': 'uni200CAtest',
        }
        response, data = self.get_response('/api/character-glyph/lock/', payload=payload)
        self.assert_response_ok(response)

    def test_0300_character_glyph_delete(self):
        # print('test_0300_character_glyph_delete')
        payload = {
            'font_uid': self.get_font_uid(),
            'name': 'uni200CAtest',
        }
        response, data = self.get_response('/api/character-glyph/delete/', payload=payload)
        self.assert_response_ok(response)

    def test_0305_character_glyph_lock_for_layer(self):
        # print('test_0305_character_glyph_lock_for_layer')
        payload = {
            'font_uid': self.get_font_uid(),
            'name': 'uni4CF2',
        }
        response, data = self.get_response('/api/character-glyph/lock/', payload=payload)
        self.assert_response_ok(response)

    def test_0310_character_glyph_layer_create_integrity_error(self):
        # print('test_0310_character_glyph_layer_create_integrity_error')
        payload = {
            'font_uid': self.get_font_uid(),
            'character_glyph_name': 'uni4CF2',
            'group_name': '20',
            'data': self.get_glif_data('character_glyph_layer_create_integrity_error/uni4CF2.glif'),
        }
        response, data = self.get_response('/api/character-glyph/layer/create/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0315_character_glyph_layer_create(self):
        # print('test_0315_character_glyph_layer_create')
        payload = {
            'font_uid': self.get_font_uid(),
            'character_glyph_name': 'uni4CF2',
            'group_name': '21',
            'data': self.get_glif_data('character_glyph_layer_create/uni4CF2.glif'),
        }
        response, data = self.get_response('/api/character-glyph/layer/create/', payload=payload)
        self.assert_response_ok(response)

    def test_0320_character_glyph_layer_rename_missing_name(self):
        # print('test_0320_character_glyph_layer_rename_missing_name')
        payload = {
            'font_uid': self.get_font_uid(),
            'character_glyph_name': 'uni4CF2',
            'group_name': '21',
            # 'new_group_name': '22',
        }
        response, data = self.get_response('/api/character-glyph/layer/rename/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0325_character_glyph_layer_rename_existing_name(self):
        # print('test_0325_character_glyph_layer_rename_existing_name')
        payload = {
            'font_uid': self.get_font_uid(),
            'character_glyph_name': 'uni4CF2',
            'group_name': '21',
            'new_group_name': '20',
        }
        response, data = self.get_response('/api/character-glyph/layer/rename/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0330_character_glyph_layer_rename(self):
        # print('test_0330_character_glyph_layer_rename')
        payload = {
            'font_uid': self.get_font_uid(),
            'character_glyph_name': 'uni4CF2',
            'group_name': '21',
            'new_group_name': '21-renamed',
        }
        response, data = self.get_response('/api/character-glyph/layer/rename/', payload=payload)
        self.assert_response_ok(response)

    def test_0335_character_glyph_layer_rename_revert(self):
        # print('test_0335_character_glyph_layer_rename_revert')
        payload = {
            'font_uid': self.get_font_uid(),
            'character_glyph_name': 'uni4CF2',
            'group_name': '21-renamed',
            'new_group_name': '21',
        }
        response, data = self.get_response('/api/character-glyph/layer/rename/', payload=payload)
        self.assert_response_ok(response)

    def test_0340_character_glyph_layer_update(self):
        # print('test_0340_character_glyph_layer_update')
        payload = {
            'font_uid': self.get_font_uid(),
            'character_glyph_name': 'uni4CF2',
            'group_name': '21',
            'data': self.get_glif_data('character_glyph_layer_update/uni4CF2.glif'),
        }
        response, data = self.get_response('/api/character-glyph/layer/update/', payload=payload)
        self.assert_response_ok(response)

    def test_0345_character_glyph_layer_delete_missing_layer_id_or_layer_name(self):
        # print('test_0345_character_glyph_layer_delete_missing_layer_id_or_layer_name')
        payload = {
            'font_uid': self.get_font_uid(),
            'character_glyph_name': 'uni4CF2',
            # 'group_name': 21,
        }
        response, data = self.get_response('/api/character-glyph/layer/delete/', payload=payload)
        self.assert_response_bad_request(response)

    def test_0350_character_glyph_layer_delete(self):
        # print('test_0350_character_glyph_layer_delete')
        payload = {
            'font_uid': self.get_font_uid(),
            'character_glyph_name': 'uni4CF2',
            'group_name': '21',
        }
        response, data = self.get_response('/api/character-glyph/layer/delete/', payload=payload)
        self.assert_response_ok(response)

    def test_0355_character_glyph_unlock_for_layer(self):
        # print('test_0355_character_glyph_unlock_for_layer')
        payload = {
            'font_uid': self.get_font_uid(),
            'name': 'uni4CF2',
        }
        response, data = self.get_response('/api/character-glyph/unlock/', payload=payload)
        self.assert_response_ok(response)

