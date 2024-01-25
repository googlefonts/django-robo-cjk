import json

from django.http import JsonResponse
from django.test import TestCase

from robocjk.api.http import (
    ApiResponseBadRequest,
    ApiResponseForbidden,
    ApiResponseInternalServerError,
    ApiResponseMethodNotAllowed,
    ApiResponseNotFound,
    ApiResponseServiceUnavailableError,
    ApiResponseSuccess,
    ApiResponseUnauthorized,
)


class HttpTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_success_response(self):
        r = ApiResponseSuccess({"message": "Hello World"})
        self.assertTrue(isinstance(r, JsonResponse))
        self.assertEqual(r.status_code, 200)
        d = json.loads(r.content)
        self.assertEqual(d["status"], r.status_code)
        self.assertEqual(d["error"], None)
        self.assertEqual(d["data"]["message"], "Hello World")

    def test_bad_request_response(self):
        m = "Error message description"
        r = ApiResponseBadRequest(m)
        self.assertTrue(isinstance(r, JsonResponse))
        self.assertEqual(r.status_code, 400)
        d = json.loads(r.content)
        self.assertEqual(d["status"], r.status_code)
        self.assertEqual(d["error"], f"Bad Request - {m}")
        self.assertEqual(d["data"], None)

    def test_unauthorized_response(self):
        m = "Error message description"
        r = ApiResponseUnauthorized(m)
        self.assertTrue(isinstance(r, JsonResponse))
        self.assertEqual(r.status_code, 401)
        d = json.loads(r.content)
        self.assertEqual(d["status"], r.status_code)
        self.assertEqual(d["error"], f"Unauthorized - {m}")
        self.assertEqual(d["data"], None)

    def test_forbidden_response(self):
        m = "Error message description"
        r = ApiResponseForbidden(m)
        self.assertTrue(isinstance(r, JsonResponse))
        self.assertEqual(r.status_code, 403)
        d = json.loads(r.content)
        self.assertEqual(d["status"], r.status_code)
        self.assertEqual(d["error"], f"Forbidden - {m}")
        self.assertEqual(d["data"], None)

    def test_not_found_response(self):
        m = "Error message description"
        r = ApiResponseNotFound(m)
        self.assertTrue(isinstance(r, JsonResponse))
        self.assertEqual(r.status_code, 404)
        d = json.loads(r.content)
        self.assertEqual(d["status"], r.status_code)
        self.assertEqual(d["error"], f"Not Found - {m}")
        self.assertEqual(d["data"], None)

    def test_method_not_allowed_response(self):
        m = "Error message description"
        r = ApiResponseMethodNotAllowed(m)
        self.assertTrue(isinstance(r, JsonResponse))
        self.assertEqual(r.status_code, 405)
        d = json.loads(r.content)
        self.assertEqual(d["status"], r.status_code)
        self.assertEqual(d["error"], f"Method Not Allowed - {m}")
        self.assertEqual(d["data"], None)

    def test_internal_server_error_response(self):
        m = "Error message description"
        r = ApiResponseInternalServerError(m)
        self.assertTrue(isinstance(r, JsonResponse))
        self.assertEqual(r.status_code, 500)
        d = json.loads(r.content)
        self.assertEqual(d["status"], r.status_code)
        self.assertEqual(d["error"], f"Internal Server Error - {m}")
        self.assertEqual(d["data"], None)

    def test_service_unavailable_error_response(self):
        m = "Error message description"
        r = ApiResponseServiceUnavailableError(m)
        self.assertTrue(isinstance(r, JsonResponse))
        self.assertEqual(r.status_code, 503)
        d = json.loads(r.content)
        self.assertEqual(d["status"], r.status_code)
        self.assertEqual(d["error"], f"Service Unavailable Error - {m}")
        self.assertEqual(d["data"], None)
