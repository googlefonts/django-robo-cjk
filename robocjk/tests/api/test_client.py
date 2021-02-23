# -*- coding: utf-8 -*-

from django.conf import settings
from django.test import TestCase
# from django.test import (
#     Client, override_settings, RequestFactory, SimpleTestCase, TestCase,
# )
from robocjk.api.client import Client


class ClientTestCase(TestCase):

    @classmethod
    def setUpTestData(self):
        # Set up data for the whole TestCase
        self._client = Client(
            host=settings.TEST_API_HOST,
            username=settings.TEST_API_USERNAME,
            password=settings.TEST_API_PASSWORD
        )
        self._project_uid = 'fde4fc80-c136-4e2f-a9be-c80e18b9f213'
        self._font_uid = 'cbac1f2d-6b6c-46a4-a477-798d49042ff4'

    def setUp(self):
        # print('setUp')
        pass

    def tearDown(self):
        # print('tearDown')
        pass

    def assert_response_ok(self, response):
        self.assertNotEqual(response, None)
        try:
            self.assertEqual(response['status'], 200)
        except AssertionError as error:
            print(response)
            raise error
        self.assertEqual(response['error'], None)
        self.assertNotEqual(response['data'], None)
        self.assertTrue(isinstance(response, (dict, list, )))

    def assert_response_error(self, response, expected_status_code):
        # print(response)
        self.assertEqual(response['status'], expected_status_code)
        self.assertNotEqual(response['error'], None)
        self.assertEqual(response['data'], None)

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

    def test_client_with_invalid_host(self):
        with self.assertRaises(ValueError):
            client = Client(
                host='http://invalid-robocjk.black-foundry.com/',
                username='admin',
                password='admin'
            )

    def test_client_with_valid_host_without_api_installed(self):
        with self.assertRaises(ValueError):
            client = Client(
                host='https://www.google.com/',
                username='admin',
                password='admin'
            )

    def test_auth_token(self):
        response = self._client.auth_token()
        # print(response)
        self.assert_response_ok(response)

    def test_user_list(self):
        response = self._client.user_list()
        # print(response)
        self.assert_response_ok(response)

    def test_user_me(self):
        response = self._client.user_me()
        # print(response)
        self.assert_response_ok(response)

    def test_project_list(self):
        response = self._client.project_list()
        # print(response)
        self.assert_response_ok(response)

    def test_project_get(self):
        response = self._client.project_get(project_uid=self._project_uid)
        # print(response)
        self.assert_response_ok(response)

    def test_font_list(self):
        response = self._client.font_list(project_uid=self._project_uid)
        # print(response)
        self.assert_response_ok(response)

    def test_font_get(self):
        response = self._client.font_get(font_uid=self._font_uid)
        # print(response)
        self.assert_response_ok(response)
        data = response['data']
        self.assertTrue(isinstance(data.get('fontlib'), dict))
        self.assertTrue(isinstance(data.get('designspace'), dict))

    def test_font_update(self):
        response = self._client.font_update(
            font_uid=self._font_uid,
            fontlib={'fontlib-test':'ok'},
            features='features-test-ok',
            designspace={'designspace-test':'ok'})
        # print(response)
        self.assert_response_ok(response)
        data = response['data']
        self.assertEqual(data.get('fontlib').get('fontlib-test'), 'ok')
        self.assertEqual(data.get('features'), 'features-test-ok')
        self.assertEqual(data.get('designspace').get('designspace-test'), 'ok')

    def test_glyphs_composition_get(self):
        response = self._client.glyphs_composition_get(font_uid=self._font_uid)
        # print(response)
        self.assert_response_ok(response)

    def test_glyphs_composition_update(self):
        response = self._client.glyphs_composition_update(font_uid=self._font_uid, data={'Glyphs-Composition-Test':'ok'})
        # print(response)
        self.assert_response_ok(response)

    def test_font_glif_list(self):
        response = self._client.glif_list(font_uid=self._font_uid)
        # print(response)
        self.assert_response_ok(response)

    def test_font_glif_lock(self):
        response = self._client.glif_lock(
            font_uid=self._font_uid,
            atomic_elements=[83, 'curvedStroke','line'],
            deep_components=['DC_2008A_00', 'DC_20041_01'],
            character_glyphs=['uni27607'])
        # print(response)
        self.assert_response_ok(response)
        self.assertEqual(len(response['data']['atomic_elements']), 2)
        self.assertEqual(len(response['data']['deep_components']), 2)
        self.assertEqual(len(response['data']['character_glyphs']), 1)

    def test_font_glif_unlock(self):
        response = self._client.glif_lock(
            font_uid=self._font_uid,
            atomic_elements=[83, 'curvedStroke','line'],
            deep_components=['DC_2008A_00', 'DC_20041_01'],
            character_glyphs=['uni27607'])
        # print(response)
        self.assert_response_ok(response)
        self.assertEqual(len(response['data']['atomic_elements']), 2)
        self.assertEqual(len(response['data']['deep_components']), 2)
        self.assertEqual(len(response['data']['character_glyphs']), 1)

    def test_atomic_element_list(self):
        response = self._client.atomic_element_list(font_uid=self._font_uid)
        # print(response)
        self.assert_response_ok(response)

    def test_atomic_element_get(self):
        response = self._client.atomic_element_get(font_uid=self._font_uid, atomic_element_id=83)
        # print(response)
        self.assert_response_ok(response)

    def test_atomic_element_lock(self):
        response = self._client.atomic_element_lock(font_uid=self._font_uid, atomic_element_id=83)
        # print(response)
        self.assert_response_ok(response)

    def test_atomic_element_unlock(self):
        response = self._client.atomic_element_unlock(font_uid=self._font_uid, atomic_element_id=83)
        # print(response)
        self.assert_response_ok(response)

    def test_deep_component_list(self):
        response = self._client.deep_component_list(font_uid=self._font_uid)
        # print(response)
        self.assert_response_ok(response)

    def test_deep_component_get(self):
        response = self._client.deep_component_get(font_uid=self._font_uid, deep_component_id=896)
        # print(response)
        self.assert_response_ok(response)

    def test_deep_component_lock(self):
        response = self._client.deep_component_lock(font_uid=self._font_uid, deep_component_id=896)
        # print(response)
        self.assert_response_ok(response)

    def test_deep_component_unlock(self):
        response = self._client.deep_component_unlock(font_uid=self._font_uid, deep_component_id=896)
        # print(response)
        self.assert_response_ok(response)

    def test_character_glyph_list(self):
        response = self._client.character_glyph_list(font_uid=self._font_uid)
        # print(response)
        self.assert_response_ok(response)

    def test_character_glyph_get(self):
        response = self._client.character_glyph_get(font_uid=self._font_uid, character_glyph_id=18627)
        # print(response)
        self.assert_response_ok(response)

    def test_character_glyph_lock(self):
        response = self._client.character_glyph_lock(font_uid=self._font_uid, character_glyph_id=18627)
        # print(response)
        self.assert_response_ok(response)

    def test_character_glyph_unlock(self):
        response = self._client.character_glyph_unlock(font_uid=self._font_uid, character_glyph_id=18627)
        # print(response)
        self.assert_response_ok(response)
