# -*- coding: utf-8 -*-

from benedict import benedict

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from functools import wraps

from robocjk.api.auth import get_user_by_auth_token_in_header
from robocjk.api.http import (
    ApiResponseBadRequest, ApiResponseUnauthorized, ApiResponseForbidden,
    ApiResponseNotFound, ApiResponseMethodNotAllowed,
    ApiResponseInternalServerError, ApiResponseServiceUnavailableError,
)
from robocjk.core import GlifData
from robocjk.models import (
    Project, Font, CharacterGlyph, CharacterGlyphLayer, DeepComponent,
    AtomicElement, AtomicElementLayer, Proof, StatusModel,
)


def api_view(view_func):
    # api_view_http_methods = ['GET', 'POST'] if settings.DEBUG else ['POST']
    api_view_http_methods = ['POST']
    @wraps(view_func)
    @csrf_exempt
    @require_http_methods(api_view_http_methods)
    def wrapper(request, *args, **kwargs):
        params = benedict(request.POST.items(), keypath_separator='/')
        # params.update(request.POST.items())
        kwargs['params'] = params
        try:
            response = view_func(request, *args, **kwargs)
        except Exception as internal_error:
            if settings.DEBUG:
                raise internal_error
            response = ApiResponseInternalServerError(str(internal_error))
        return response
    wrapper.__dict__['api_view'] = True
    return wrapper


def require_params(**required_params):
    def decorator(view_func, *args, **kwargs):
        @wraps(view_func)
        def inner(request, *args, **kwargs):
            params = kwargs['params']
            for param_key, param_type in required_params.items():
                method_name = 'get_{}'.format(param_type)
                method = getattr(params, method_name, None)
                if method is None:
                    raise ValueError('Invalid param type: \'{}\''.format(param_type))
                value = method(param_key, default=None)
                if value is None:
                    return ApiResponseBadRequest(
                        'Invalid or missing parameter \'{}\'.'.format(param_key, param_type))
                params[param_key] = value
            return view_func(request, *args, **kwargs)
        return inner
    decorator.__dict__['require_params'] = True
    return decorator


def require_user(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = get_user_by_auth_token_in_header(request)# or request.user
        # if user and user.is_authenticated and user.is_active:
        if user and user.is_active:
            kwargs['user'] = user
            return view_func(request, *args, **kwargs)
        return ApiResponseUnauthorized(
            'This resource is accessible only upon authentication.')
    wrapper.__dict__['require_user'] = True
    return wrapper


def require_project(view_func):
    @wraps(view_func)
    @require_params(project_uid='str')
    def wrapper(request, *args, **kwargs):
        # build query filters
        params = kwargs['params']
        project_uid = params.get_uuid('project_uid')
        if not project_uid:
            return ApiResponseBadRequest(
                'Missing or invalid parameter \'{}project_uid\'.')
        try:
            project_obj = Project.objects.get(uid=project_uid)
        except Project.DoesNotExist:
            return ApiResponseNotFound(
                'Project object with \'project_uid={}\' not found.'.format(project_uid))
        # success
        kwargs['project'] = project_obj
        return view_func(request, *args, **kwargs)
    wrapper.__dict__['require_project'] = True
    return wrapper


def require_font(view_func):
    @wraps(view_func)
    @require_params(font_uid='str')
    def wrapper(request, *args, **kwargs):
        # build query filters
        params = kwargs['params']
        font_uid = params.get_uuid('font_uid')
        if not font_uid:
            return ApiResponseBadRequest(
                'Missing or invalid parameter \'{}font_uid\'.')
        try:
            font_obj = Font.objects.get(uid=font_uid)
        except Font.DoesNotExist:
            return ApiResponseNotFound(
                'Font object with \'font_uid={}\' not found.'.format(font_uid))
        if not font_obj.available:
            return ApiResponseServiceUnavailableError(
                'Font object with \'font_uid={}\' is temporary not available due to some maintenance.')
        # success
        kwargs['font'] = font_obj
        return view_func(request, *args, **kwargs)
    wrapper.__dict__['require_font'] = True
    return wrapper


def require_glif_filters(view_func):
    @wraps(view_func)
    @require_font
    def wrapper(request, *args, **kwargs):
        # build query filters
        user = kwargs['user']
        font = kwargs['font']
        params = kwargs['params']
        filters = benedict({
            'font_id': font.id,
            'status': params.get_str('status', None),
            'locked_by_id': user.id if params.get_bool('is_locked_by_current_user', False) else None,
            'is_locked': params.get_bool('is_locked', None),
            'is_empty': params.get_bool('is_empty', None),
            'has_variation_axis': params.get_bool('has_variation_axis', None),
            'has_outlines': params.get_bool('has_outlines', None),
            'has_components': params.get_bool('has_components', None),
            'has_unicode': params.get_bool('has_unicode', None),
        })
        filters.clean()
        kwargs['glif_filters'] = filters
        return view_func(request, *args, **kwargs)
    wrapper.__dict__['require_glif_filters'] = True
    return wrapper


def require_data(view_func):
    @wraps(view_func)
    @require_params(data='str')
    def wrapper(request, *args, **kwargs):
        params = kwargs['params']
        data = params.get_str('data')
        # parse and validate glif xml data
        glif = GlifData()
        glif.parse_string(data)
        if not glif.ok:
            return ApiResponseBadRequest(
                'Invalid parameter "data", data must be a valid .glif xml file - {}.'.format(str(glif.error)))
        # success
        kwargs['data'] = data
        kwargs['glif'] = glif
        return view_func(request, *args, **kwargs)
    wrapper.__dict__['require_data'] = True
    return wrapper


# def require_data_or_name(view_func):
#     @wraps(view_func)
#     def wrapper(request, *args, **kwargs):
#         params = kwargs['params']
#         data = params.get_str('data')
#         glif = None
#         name = params.get_str('name')
#         if (data and name) or (not data and not name):
#             return ApiResponseBadRequest(
#                 'Invalid parameter "data" / "name", data or name are required and are mutually exclusive.')
#         if data:
#             # parse and validate glif xml data
#             glif = GlifData()
#             glif.parse_string(data)
#             if not glif.ok:
#                 return ApiResponseBadRequest(
#                     'Invalid parameter "data", data must be a valid .glif xml file - {}.'.format(str(glif.error)))
#         # success
#         kwargs['data'] = data
#         kwargs['glif'] = glif
#         # kwargs['name'] = name
#         return view_func(request, *args, **kwargs)
#     wrapper.__dict__['require_data'] = True
#     return wrapper


def require_status(view_func):
    @wraps(view_func)
    @require_params(status='str')
    def wrapper(request, *args, **kwargs):
        params = kwargs['params']
        status_choices = StatusModel.STATUS_CHOICES_VALUES_LIST
        status = params.get_str('status', choices=status_choices, default='')
        if not status:
            return ApiResponseBadRequest(
                'Invalid parameter "status", status value must be "{}".'.format('" or "'.join(status_choices)))
        # success
        kwargs['status'] = status
        return view_func(request, *args, **kwargs)
    wrapper.__dict__['require_status'] = True
    return wrapper


def require_atomic_element(**kwargs):
    # read decorator options
    select_related = kwargs.get('select_related', ['locked_by']) or []
    prefetch_related = kwargs.get('prefetch_related', ['layers', 'deep_components']) or []
    prefix_params = kwargs.get('prefix_params', False)
    check_locked = kwargs.get('check_locked', False)
    def decorator(view_func, *args, **kwargs):
        @wraps(view_func)
        @require_font
        def inner(request, *args, **kwargs):
            # build query filters
            params = kwargs['params']
            prefix = 'atomic_element_' if prefix_params else ''
            filters = benedict({
                'id': params.get_int('{}id'.format(prefix), None),
                'name': params.get_str('{}name'.format(prefix), None),
            })
            filters.clean()
            if not filters:
                return ApiResponseBadRequest(
                    'Missing parameter \'{}id\' or \'{}name\'.'.format(prefix, prefix))
            filters['font_id'] = kwargs['font'].id
            # retrieve atomic element object
            obj_cls = AtomicElement
            try:
                obj = obj_cls.objects.select_related(*select_related).prefetch_related(*prefetch_related).get(**filters)
            except obj_cls.DoesNotExist:
                return ApiResponseNotFound(
                    'Atomic Element object with \'{}\' not found.'.format(filters))
            except obj_cls.MultipleObjectsReturned:
                return ApiResponseInternalServerError()
            # check lock
            user = kwargs['user']
            if check_locked:
                if not obj.is_lockable_by(user):
                    return ApiResponseForbidden(
                        'Atomic Element object has already been locked by another user.')
                if not obj.is_locked_by(user):
                    return ApiResponseForbidden(
                        'Atomic Element object must be locked by the current user.')
            # success
            kwargs['atomic_element'] = obj
            return view_func(request, *args, **kwargs)
        return inner
    decorator.__dict__['require_atomic_element'] = True
    return decorator


def require_atomic_element_layer(**kwargs):
    # read decorator options
    prefix_params = kwargs.get('prefix_params', False)
    def decorator(view_func, *args, **kwargs):
        @wraps(view_func)
        @require_atomic_element(check_locked=True, prefix_params=True)
        def inner(request, *args, **kwargs):
            # build query filters
            params = kwargs['params']
            prefix = 'layer_' if prefix_params else ''
            filters = benedict({
                'id': params.get_int('{}id'.format(prefix), None),
                'group_name': params.get_str('{}group_name'.format(prefix), None),
            })
            filters.clean()
            if not filters:
                return ApiResponseBadRequest(
                    'Missing parameter \'{}id\' or \'{}group_name\'.'.format(prefix, prefix))
            # retrieve atomic element layer object
            atomic_element = kwargs['atomic_element']
            obj_cls = AtomicElementLayer
            try:
                obj = atomic_element.layers.get(**filters)
            except obj_cls.DoesNotExist:
                return ApiResponseNotFound(
                    'Atomic Element Layer object with \'{}\' not found.'.format(filters))
            except obj_cls.MultipleObjectsReturned:
                return ApiResponseInternalServerError()
            # success
            kwargs['atomic_element_layer'] = obj
            return view_func(request, *args, **kwargs)
        return inner
    decorator.__dict__['require_atomic_element_layer'] = True
    return decorator


def require_deep_component(**kwargs):
    # read decorator options
    select_related = kwargs.get('select_related', ['locked_by']) or []
    prefetch_related = kwargs.get('prefetch_related', ['character_glyphs', 'atomic_elements']) or []
    prefix_params = kwargs.get('prefix_params', False)
    check_locked = kwargs.get('check_locked', False)
    def decorator(view_func, *args, **kwargs):
        @wraps(view_func)
        @require_font
        def inner(request, *args, **kwargs):
            # build query filters
            params = kwargs['params']
            prefix = 'deep_component_' if prefix_params else ''
            filters = benedict({
                'id': params.get_int('{}id'.format(prefix), None),
                'name': params.get_str('{}name'.format(prefix), None),
            })
            filters.clean()
            if not filters:
                return ApiResponseBadRequest(
                    'Missing parameter \'{}id\' or \'{}name\'.'.format(prefix, prefix))
            filters['font_id'] = kwargs['font'].id
            # retrieve deep component object
            obj_cls = DeepComponent
            try:
                obj = obj_cls.objects.select_related(*select_related).prefetch_related(*prefetch_related).get(**filters)
            except obj_cls.DoesNotExist:
                return ApiResponseNotFound(
                    'Deep Component object with \'{}\' not found.'.format(filters))
            except obj_cls.MultipleObjectsReturned:
                return ApiResponseInternalServerError()
            # check lock
            user = kwargs['user']
            if check_locked:
                if not obj.is_lockable_by(user):
                    return ApiResponseForbidden(
                        'Deep Component object has already been locked by another user.')
                if not obj.is_locked_by(user):
                    return ApiResponseForbidden(
                        'Deep Component object must be locked by the current user.')
            # success
            kwargs['deep_component'] = obj
            return view_func(request, *args, **kwargs)
        return inner
    decorator.__dict__['require_deep_component'] = True
    return decorator


def require_character_glyph(**kwargs):
    # read decorator options
    select_related = kwargs.get('select_related', ['locked_by']) or []
    prefetch_related = kwargs.get('prefetch_related', ['layers', 'deep_components']) or []
    prefix_params = kwargs.get('prefix_params', False)
    check_locked = kwargs.get('check_locked', False)
    def decorator(view_func, *args, **kwargs):
        @wraps(view_func)
        @require_font
        def inner(request, *args, **kwargs):
            # build query filters
            params = kwargs['params']
            prefix = 'character_glyph_' if prefix_params else ''
            filters = benedict({
                'id': params.get_int('{}id'.format(prefix), None),
                'name': params.get_str('{}name'.format(prefix), None),
                'unicode_hex': params.get_str('{}unicode_hex'.format(prefix), None),
            })
            filters.clean()
            if not filters:
                return ApiResponseBadRequest(
                    'Missing parameter \'{}id\' or \'{}name\' or \'{}unicode_hex\'.'.format(prefix, prefix, prefix))
            filters['font_id'] = kwargs['font'].id
            # retrieve character glyph objecs
            obj_cls = CharacterGlyph
            try:
                obj = obj_cls.objects.select_related(*select_related).prefetch_related(*prefetch_related).get(**filters)
            except obj_cls.DoesNotExist:
                return ApiResponseNotFound(
                    'Character Glyph object with \'{}\' not found.'.format(filters))
            except obj_cls.MultipleObjectsReturned:
                return ApiResponseInternalServerError()
            # check lock
            user = kwargs['user']
            if check_locked:
                if not obj.is_lockable_by(user):
                    return ApiResponseForbidden(
                        'Character Glyph object has been locked by another user.')
                if not obj.is_locked_by(user):
                    return ApiResponseForbidden(
                        'Character Glyph object must be locked by the current user.')
            # success
            kwargs['character_glyph'] = obj
            return view_func(request, *args, **kwargs)
        return inner
    decorator.__dict__['require_character_glyph'] = True
    return decorator


def require_character_glyph_layer(**kwargs):
    # read decorator options
    prefix_params = kwargs.get('prefix_params', False)
    def decorator(view_func, *args, **kwargs):
        @wraps(view_func)
        @require_character_glyph(check_locked=True, prefix_params=True)
        def inner(request, *args, **kwargs):
            # build query filters
            params = kwargs['params']
            prefix = 'layer_' if prefix_params else ''
            filters = benedict({
                'id': params.get_int('{}id'.format(prefix), None),
                'group_name': params.get_str('{}group_name'.format(prefix), None),
            })
            filters.clean()
            if not filters:
                return ApiResponseBadRequest(
                    'Missing parameter \'{}id\' or \'{}group_name\'.'.format(prefix, prefix))
            # retrieve character glyph layer object
            character_glyph = kwargs['character_glyph']
            obj_cls = CharacterGlyphLayer
            try:
                obj = character_glyph.layers.get(**filters)
            except obj_cls.DoesNotExist:
                return ApiResponseNotFound(
                    'Character Glyph Layer object with \'{}\' not found.'.format(filters))
            except obj_cls.MultipleObjectsReturned:
                return ApiResponseInternalServerError()
            # success
            kwargs['character_glyph_layer'] = obj
            return view_func(request, *args, **kwargs)
        return inner
    decorator.__dict__['require_character_glyph_layer'] = True
    return decorator

