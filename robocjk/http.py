# -*- coding: utf-8 -*-

from django.http import JsonResponse


class ApiResponse(JsonResponse):

    def __init__(self, data=None, status=None, error=None):
        d = {
            'data': data,
            'status': status,
            'error': error,
        }
        super(ApiResponse, self).__init__(d)


class ApiResponseSuccess(ApiResponse):

    def __init__(self, data):
        d = {
            'data': data,
            'status': 200,
            'error': None,
        }
        super(ApiResponseSuccess, self).__init__(d)


class ApiResponseError(ApiResponse):

    # 400 Bad Request - The server cannot or will not process the request due to an apparent client error (e.g., malformed request syntax, size too large, invalid request message framing, or deceptive request routing).
    # 401 Unauthorized - Similar to 403 Forbidden, but specifically for use when authentication is required and has failed or has not yet been provided
    # 403 Forbidden - The request contained valid data and was understood by the server, but the server is refusing action
    # 404 Not Found - The requested resource could not be found but may be available in the future. Subsequent requests by the client are permissible.
    # 405 Method Not Allowed - A request method is not supported for the requested resource

    def __init__(self, status, error):
        super(ApiResponseError, self).__init__(
            status=status, error=error)


class ApiResponseBadRequest(ApiResponseError):

    def __init__(self, error=''):
        super(ApiResponseBadRequest, self).__init__(
            status=400, error='Bad Request - {}'.format(error))


class ApiResponseUnauthorized(ApiResponseError):

    def __init__(self, error=''):
        super(ApiResponseUnauthorized, self).__init__(
            status=401, error='Unauthorized - {}'.format(error))


class ApiResponseForbidden(ApiResponseError):

    def __init__(self, error=''):
        super(ApiResponseForbidden, self).__init__(
            status=403, error='Forbidden - {}'.format(error))


class ApiResponseNotFound(ApiResponseError):

    def __init__(self, error=''):
        super(ApiResponseNotFound, self).__init__(
            status=404, error='Not Found - {}'.format(error))


class ApiResponseMethodNotAllowed(ApiResponseError):

    def __init__(self, error=''):
        super(ApiResponseMethodNotAllowed, self).__init__(
            status=405, error='Method Not Allowed - {}'.format(error))


class ApiResponseInternalServerError(ApiResponseError):

    def __init__(self, error=''):
        super(ApiResponseInternalServerError, self).__init__(
            status=500, error='Internal Server Error - {}'.format(error))


def get_object_response(data):
    data = data or []
    count = len(data)
    if count == 0:
        return ApiResponseNotFound()
    elif count > 1:
        return ApiResponseBadRequest()
    return ApiResponseSuccess(data[0])


def get_objects_list_response(data):
    return ApiResponseSuccess(data)

