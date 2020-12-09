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

    def test_auth_token(self):
        data = self._client.auth_token()
        # print(data)
        self.assert_response_ok(data)

    def test_user_list(self):
        data = self._client.user_list()
        # print(data)
        self.assert_response_ok(data)

    def test_user_me(self):
        data = self._client.user_me()
        # print(data)
        self.assert_response_ok(data)

    def test_project_list(self):
        data = self._client.project_list()
        # print(data)
        self.assert_response_ok(data)

    def test_project_get(self):
        data = self._client.project_get(project_uid=self._project_uid)
        # print(data)
        self.assert_response_ok(data)

    def test_font_list(self):
        data = self._client.font_list(project_uid=self._project_uid)
        # print(data)
        self.assert_response_ok(data)

    def test_font_get(self):
        data = self._client.font_get(font_uid=self._font_uid)
        # print(data)
        self.assert_response_ok(data)

    def test_font_glif_list(self):
        data = self._client.glif_list(font_uid=self._font_uid)
        # print(data)
        self.assert_response_ok(data)

    def test_atomic_element_list(self):
        data = self._client.atomic_element_list(font_uid=self._font_uid)
        # print(data)
        self.assert_response_ok(data)

    def test_atomic_element_get(self):
        data = self._client.atomic_element_get(font_uid=self._font_uid, atomic_element_id=83)
        # print(data)
        self.assert_response_ok(data)

    def test_atomic_element_lock(self):
        data = self._client.atomic_element_lock(font_uid=self._font_uid, atomic_element_id=83)
        # print(data)
        self.assert_response_ok(data)

    def test_atomic_element_unlock(self):
        data = self._client.atomic_element_unlock(font_uid=self._font_uid, atomic_element_id=83)
        # print(data)
        self.assert_response_ok(data)

    def test_deep_component_list(self):
        data = self._client.deep_component_list(font_uid=self._font_uid)
        # print(data)
        self.assert_response_ok(data)

    def test_deep_component_get(self):
        data = self._client.deep_component_get(font_uid=self._font_uid, deep_component_id=896)
        # print(data)
        self.assert_response_ok(data)

    def test_deep_component_lock(self):
        data = self._client.deep_component_lock(font_uid=self._font_uid, deep_component_id=896)
        # print(data)
        self.assert_response_ok(data)

    def test_deep_component_unlock(self):
        data = self._client.deep_component_unlock(font_uid=self._font_uid, deep_component_id=896)
        # print(data)
        self.assert_response_ok(data)

    def test_character_glyph_list(self):
        data = self._client.character_glyph_list(font_uid=self._font_uid)
        # print(data)
        self.assert_response_ok(data)

    def test_character_glyph_get(self):
        data = self._client.character_glyph_get(font_uid=self._font_uid, character_glyph_id=18627)
        # print(data)
        self.assert_response_ok(data)

    def test_character_glyph_lock(self):
        data = self._client.character_glyph_lock(font_uid=self._font_uid, character_glyph_id=18627)
        # print(data)
        self.assert_response_ok(data)

    def test_character_glyph_unlock(self):
        data = self._client.character_glyph_unlock(font_uid=self._font_uid, character_glyph_id=18627)
        # print(data)
        self.assert_response_ok(data)
