# -*- coding: utf-8 -*-

from django.test import TestCase

from robocjk.api.auth import encode_auth_token, decode_auth_token, generate_auth_token


class AuthTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_encode_auth_token(self):
        data = { 'message':'Hello World' }
        token = encode_auth_token(data)
        self.assertEqual(token, 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJtZXNzYWdlIjoiSGVsbG8gV29ybGQifQ.6YMHbUtNNnRwRn9L2Z6llQ28G5AZaLqwvzdtyhWBJP0')

    def test_decode_auth_token(self):
        token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJtZXNzYWdlIjoiSGVsbG8gV29ybGQifQ.6YMHbUtNNnRwRn9L2Z6llQ28G5AZaLqwvzdtyhWBJP0'
        data = decode_auth_token(token)
        self.assertEqual(data, { 'message':'Hello World' })

    def test_generate_auth_token(self):
        data = { 'message':'Hello World' }
        token_encoded = generate_auth_token({ 'days':5 }, data)
        token_decoded = decode_auth_token(token_encoded)
        self.assertEqual(token_decoded['message'], data['message'])
