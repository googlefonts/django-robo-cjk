# -*- coding: utf-8 -*-

from django.contrib.auth import authenticate, login, logout

from robocjk.api.auth import get_auth_token

from robocjk.api.decorators import (
    api_view,
    require_params,
    require_user,
    require_data,
    require_font,
    require_glif_filters,
    require_atomic_element,
    require_atomic_element_layer,
    require_deep_component,
    require_character_glyph,
    require_character_glyph_layer, )

from robocjk.api.http import (
    ApiResponseBadRequest, ApiResponseUnauthorized,
    ApiResponseForbidden, ApiResponseNotFound,
    ApiResponseMethodNotAllowed, ApiResponseInternalServerError,
    ApiResponseSuccess, )

from robocjk.core import GlifData

from robocjk.models import (
    Project, Font, CharacterGlyph, CharacterGlyphLayer,
    DeepComponent, AtomicElement, AtomicElementLayer, Proof, )


@api_view
def auth_token(request, params, *args, **kwargs):
    username = params.get_str('username')
    password = params.get_str('password')
    if not username or not password:
        return ApiResponseBadRequest(
            'Unable to generate auth token, missing username and/or password parameters.')
    token = get_auth_token(request, username, password, expiration={'days':1 })
    if token is None:
        return ApiResponseBadRequest(
            'Unable to generate auth token, invalid credentials.')
    data = {
        'auth_token': token,
        'refresh_token': None, # TODO
    }
    return ApiResponseSuccess(data)


def auth_refresh_token(request, *args, **kwargs):
    # TODO
    pass


@api_view
@require_user
def project_list(request, params, *args, **kwargs):
    data = list(Project.objects.values('id', 'name', 'slug', 'repo_url'))
    return ApiResponseSuccess(data)


@api_view
@require_user
def font_list(request, params, *args, **kwargs):
    data = list(Font.objects.values('project_id', 'id', 'name', 'slug', 'fontlib'))
    return ApiResponseSuccess(data)


@api_view
@require_user
@require_glif_filters
def glif_list(request, glif_filters, *args, **kwargs):
    data = {
        'atomic_elements': list(AtomicElement.objects.filter(**glif_filters).values('id', 'name')),
        'deep_components': list(DeepComponent.objects.filter(**glif_filters).values('id', 'name')),
        'character_glyphs': list(CharacterGlyph.objects.filter(**glif_filters).values('id', 'name', 'unicode_hex')),
    }
    return ApiResponseSuccess(data)


@api_view
@require_user
@require_glif_filters
def atomic_element_list(request, glif_filters, *args, **kwargs):
    data = list(AtomicElement.objects.filter(**glif_filters).values('id', 'name'))
    return ApiResponseSuccess(data)


@api_view
@require_user
@require_atomic_element()
def atomic_element_get(request, atomic_element, *args, **kwargs):
    return ApiResponseSuccess(atomic_element.serialize())


@api_view
@require_user
@require_font
@require_data
def atomic_element_create(request, font, data, glif, *args, **kwargs):
    filters = { 'font_id':font.id, 'name':glif.name }
    atomic_element, atomic_element_created = AtomicElement.objects.get_or_create(defaults={ 'data':data }, **filters)
    if not atomic_element_created:
        return ApiResponseBadRequest(
            'Atomic Element with font_id=\'{}\' and name=\'{}\' already exists.'.format(font.id, glif.name))
    return ApiResponseSuccess(atomic_element.serialize())


@api_view
@require_user
@require_atomic_element(check_locked=True)
@require_data
def atomic_element_update(request, atomic_element, data, glif, *args, **kwargs):
    atomic_element.data = data
    atomic_element.save()
    return ApiResponseSuccess(atomic_element.serialize())


@api_view
@require_user
@require_atomic_element(check_locked=True)
def atomic_element_delete(request, atomic_element, *args, **kwargs):
    return ApiResponseSuccess(atomic_element.delete())


@api_view
@require_user
@require_atomic_element()
def atomic_element_lock(request, atomic_element, *args, **kwargs):
    if atomic_element.lock_by(request.user):
        return ApiResponseSuccess(atomic_element.serialize())
    return ApiResponseForbidden(
        'Atomic Element can\'t be locked, it has already been locked by another user.')


@api_view
@require_user
@require_atomic_element()
def atomic_element_unlock(request, atomic_element, *args, **kwargs):
    if atomic_element.unlock_by(request.user):
        return ApiResponseSuccess(atomic_element.serialize())
    return ApiResponseForbidden(
        'Atomic Element can\'t be unlocked, it has been locked by another user.')


@api_view
@require_user
@require_atomic_element(check_locked=True, prefix_params=True)
@require_data
@require_params(group_name='str')
def atomic_element_layer_create(request, font, atomic_element, data, glif, params, *args, **kwargs):
    group_name = params.get('group_name')
    options = {
        'glif_id': atomic_element.id,
        'group_name': group_name,
        'defaults': {
            'data': data,
        },
    }
    layer, layer_created = AtomicElementLayer.objects.get_or_create(**options)
    if not layer_created:
        return ApiResponseBadRequest(
            'Atomic Element Layer with font_id=\'{}\', glif_id=\'{}\', ' \
            'glif__name=\'{}\' group_name=\'{}\' already exists.'.format(
                font.id, atomic_element.id, atomic_element.name, group_name))
    return ApiResponseSuccess(atomic_element.serialize())


@api_view
@require_user
@require_atomic_element_layer()
@require_data
def atomic_element_layer_update(request, atomic_element, atomic_element_layer, data, *args, **kwargs):
    atomic_element_layer.data = data
    atomic_element_layer.save()
    return ApiResponseSuccess(atomic_element.serialize())


@api_view
@require_user
@require_atomic_element_layer()
def atomic_element_layer_delete(request, atomic_element_layer, *args, **kwargs):
    return ApiResponseSuccess(atomic_element_layer.delete())


@api_view
@require_user
@require_glif_filters
def deep_component_list(request, glif_filters, *args, **kwargs):
    data = list(DeepComponent.objects.filter(**glif_filters).values('id', 'name'))
    return ApiResponseSuccess(data)


@api_view
@require_user
@require_deep_component()
def deep_component_get(request, deep_component, *args, **kwargs):
    return ApiResponseSuccess(deep_component.serialize())


@api_view
@require_user
@require_font
@require_data
def deep_component_create(request, font, data, glif, *args, **kwargs):
    filters = { 'font_id':font.id, 'name':glif.name }
    deep_component, deep_component_created = DeepComponent.objects.get_or_create(defaults={ 'data':data }, **filters)
    if not deep_component_created:
        return ApiResponseBadRequest(
            'Deep Component with font_id=\'{}\' and name=\'{}\' already exists.'.format(font.id, glif.name))
    return ApiResponseSuccess(deep_component.serialize())


@api_view
@require_user
@require_deep_component(check_locked=True)
@require_data
def deep_component_update(request, deep_component, data, glif, *args, **kwargs):
    deep_component.data = data
    deep_component.save()
    return ApiResponseSuccess(deep_component.serialize())


@api_view
@require_user
@require_deep_component(check_locked=True)
def deep_component_delete(request, deep_component, *args, **kwargs):
    return ApiResponseSuccess(deep_component.delete())


@api_view
@require_user
@require_deep_component()
def deep_component_lock(request, deep_component, *args, **kwargs):
    if deep_component.lock_by(request.user):
        return ApiResponseSuccess(deep_component.serialize())
    return ApiResponseForbidden(
        'Deep Component can\'t be locked, it has already been locked by another user.')


@api_view
@require_user
@require_deep_component()
def deep_component_unlock(request, deep_component, *args, **kwargs):
    if deep_component.unlock_by(request.user):
        return ApiResponseSuccess(deep_component.serialize())
    return ApiResponseForbidden(
        'Deep Component can\'t be unlocked, it has been locked by another user.')


@api_view
@require_user
@require_glif_filters
def character_glyph_list(request, glif_filters, *args, **kwargs):
    data = list(CharacterGlyph.objects.filter(**glif_filters).values('id', 'name', 'unicode_hex'))
    return ApiResponseSuccess(data)


@api_view
@require_user
@require_character_glyph(select_related=['locked_by'], prefetch_related=['layers', 'deep_components'])
def character_glyph_get(request, character_glyph, *args, **kwargs):
    return ApiResponseSuccess(character_glyph.serialize())


@api_view
@require_user
@require_font
@require_data
def character_glyph_create(request, font, data, glif, *args, **kwargs):
    filters = { 'font_id':font.id, 'name':glif.name }
    character_glyph, character_glyph_created = CharacterGlyph.objects.get_or_create(defaults={ 'data':data }, **filters)
    if not character_glyph_created:
        return ApiResponseBadRequest(
            'Character Glyph with font_id=\'{}\' and name=\'{}\' already exists.'.format(font.id, glif.name))
    return ApiResponseSuccess(character_glyph.serialize())


@api_view
@require_user
@require_character_glyph(check_locked=True)
@require_data
def character_glyph_update(request, character_glyph, data, glif, *args, **kwargs):
    # TODO: check lock
    character_glyph.data = data
    character_glyph.save()
    return ApiResponseSuccess(character_glyph.serialize())


@api_view
@require_user
@require_character_glyph(check_locked=True)
def character_glyph_delete(request, character_glyph, *args, **kwargs):
    return ApiResponseSuccess(character_glyph.delete())


@api_view
@require_user
@require_character_glyph()
def character_glyph_lock(request, character_glyph, *args, **kwargs):
    if character_glyph.lock_by(request.user):
        return ApiResponseSuccess(character_glyph.serialize())
    return ApiResponseForbidden(
        'Character Glyph can\'t be locked, it has already been locked by another user.')


@api_view
@require_user
@require_character_glyph()
def character_glyph_unlock(request, character_glyph, *args, **kwargs):
    if character_glyph.unlock_by(request.user):
        return ApiResponseSuccess(character_glyph.serialize())
    return ApiResponseForbidden(
        'Character Glyph can\'t be unlocked, it has been locked by another user.')


@api_view
@require_user
@require_character_glyph(prefix_params=True)
@require_data
@require_params(group_name='str')
def character_glyph_layer_create(request, font, character_glyph, data, glif, *args, **kwargs):
    params = kwargs['params']
    group_name = params.get('group_name')
    options = {
        'glif_id': character_glyph.id,
        'group_name': group_name,
        'defaults': {
            'data': data,
        },
    }
    layer, layer_created = CharacterGlyphLayer.objects.get_or_create(**options)
    if not layer_created:
        return ApiResponseBadRequest(
            'Character Glyph Layer with font_id=\'{}\', glif_id=\'{}\', glif__name=\'{}\', group_name=\'{}\' already exists.'.format(
                font.id, character_glyph.id, character_glyph.name, group_name))
    return ApiResponseSuccess(character_glyph.serialize())


@api_view
@require_user
@require_character_glyph_layer()
@require_data
def character_glyph_layer_update(request, character_glyph, character_glyph_layer, data, *args, **kwargs):
    params = kwargs['params']
    character_glyph_layer.data = data
    character_glyph_layer.save()
    return ApiResponseSuccess(character_glyph.serialize())


@api_view
@require_user
@require_character_glyph_layer()
def character_glyph_layer_delete(request, character_glyph_layer, *args, **kwargs):
    return ApiResponseSuccess(character_glyph_layer.delete())

