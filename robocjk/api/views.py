# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.core.exceptions import ValidationError

from robocjk.api.auth import get_auth_token
from robocjk.api.decorators import (
    api_view,
    require_params,
    require_user,
    require_data,
    require_status,
    require_project,
    require_font,
    require_glif_filters,
    require_atomic_element,
    require_atomic_element_layer,
    require_deep_component,
    require_character_glyph,
    require_character_glyph_layer,
)
from robocjk.api.http import (
    ApiResponseBadRequest, ApiResponseUnauthorized,
    ApiResponseForbidden, ApiResponseNotFound,
    ApiResponseMethodNotAllowed, ApiResponseInternalServerError,
    ApiResponseSuccess,
)
from robocjk.api.serializers import (
    USER_FIELDS,
    PROJECT_FIELDS,
    FONT_FIELDS,
    ATOMIC_ELEMENT_ID_FIELDS,
    DEEP_COMPONENT_ID_FIELDS,
    CHARACTER_GLYPH_ID_FIELDS,
    serialize_user,
)
from robocjk.core import GlifData
from robocjk.models import (
    repo_ssh_url_validator,
    Project, Font, GlyphsComposition,
    CharacterGlyph, CharacterGlyphLayer,
    DeepComponent,
    AtomicElement, AtomicElementLayer,
    Proof, )
from robocjk.settings import API_AUTH_TOKEN_EXPIRATION


UserClass = get_user_model()


@api_view
def auth_token(request, params, *args, **kwargs):
    username = params.get_str('username')
    password = params.get_str('password')
    if not username or not password:
        return ApiResponseBadRequest(
            'Unable to generate auth token, missing username and/or password parameters.')
    token = get_auth_token(request, username, password, expiration=API_AUTH_TOKEN_EXPIRATION)
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
def user_list(request, params, *args, **kwargs):
    data = list(UserClass.objects.values(*USER_FIELDS))
    return ApiResponseSuccess(data)


# @api_view
# @require_user
# def user_get(request, params, *args, **kwargs):
#     data = {} # list(Project.objects.values(*PROJECT_FIELDS))
#     return ApiResponseSuccess(data)


@api_view
@require_user
def user_me(request, params, user, *args, **kwargs):
    data = serialize_user(user)
    return ApiResponseSuccess(data)


@api_view
@require_user
def project_list(request, params, *args, **kwargs):
    data = list(Project.objects.values(*PROJECT_FIELDS))
    return ApiResponseSuccess(data)


@api_view
@require_user
@require_project
def project_get(request, project, *args, **kwargs):
    return ApiResponseSuccess(project.serialize())


@api_view
@require_user
@require_params(name='str', repo_url='str')
def project_create(request, params, *args, **kwargs):
    name = params.get_str('name')
    repo_url = params.get_str('repo_url')
    try:
        repo_ssh_url_validator(repo_url)
    except ValidationError as repo_url_error:
        return ApiResponseBadRequest(
            'Invalid parameter \'repo_url\': {} -> {}'.format(repo_url, repo_url_error.message))
    if Project.objects.filter(name__iexact=name).exists():
        return ApiResponseBadRequest(
            'Project with name=\'{}\' already exists, ' \
            'please choose a different name.'.format(name))
    if Project.objects.filter(repo_url__iexact=repo_url).exists():
        return ApiResponseBadRequest(
            'Project with repo_url=\'{}\' already exists, ' \
            'please choose a different repository url.'.format(repo_url))
    project = Project()
    project.name = name
    project.repo_url = repo_url
    project.save()
    return ApiResponseSuccess(project.serialize())


# @api_view
# @require_user
# @require_project
# @require_params(name='str')
# def project_rename(request, params, project, *args, **kwargs):
#     name = params.get_str('name')
#     if Project.objects.filter(name__iexact=name).exclude(id=project.id).exists():
#         return ApiResponseBadRequest(
#             'Project with name=\'{}\' already exists, ' \
#             'please choose a different name.'.format(name))
#     project.name = name
#     project.save()
#     return ApiResponseSuccess(project.serialize())


@api_view
@require_user
@require_project
def project_delete(request, user, project, *args, **kwargs):
    if not user.is_superuser:
        return ApiResponseForbidden('Only super-users are allowed to delete projects.')
    return ApiResponseSuccess(project.delete())


@api_view
@require_user
@require_project
def font_list(request, user, project, *args, **kwargs):
    font_fields = set(FONT_FIELDS)
    font_fields.remove('fontlib')
    font_fields = list(font_fields)
    data = list(Font.objects.filter(project_id=project.id).values(*font_fields))
    return ApiResponseSuccess(data)


@api_view
@require_user
@require_font
def font_get(request, font, *args, **kwargs):
    return ApiResponseSuccess(font.serialize())


@api_view
@require_user
@require_project
@require_params(name='str')
def font_create(request, params, *args, **kwargs):
    project = kwargs['project']
    name = params.get_str('name')
    if Font.objects.filter(name__iexact=name).exists():
        return ApiResponseBadRequest(
            'Font with name=\'{}\' already exists, ' \
            'please choose a different name.'.format(name))
    font = Font()
    font.project = project
    font.name = name
    font.fontlib = params.get_dict('fontlib')
    font.save()
    return ApiResponseSuccess(font.serialize())


@api_view
@require_user
@require_font
def font_update(request, user, params, font, *args, **kwargs):
    font_changed = False
    # look for fontlib data
    fontlib = params.get_dict('fontlib')
    if fontlib:
        font.fontlib = fontlib
        font_changed = True
    # font is changed, save it
    if font_changed:
        font.save_by(user)
    return ApiResponseSuccess(font.serialize())


@api_view
@require_user
@require_font
def font_delete(request, user, font, *args, **kwargs):
    if not user.is_superuser:
        return ApiResponseForbidden('Only super-users are allowed to delete fonts.')
    return ApiResponseSuccess(font.delete())


@api_view
@require_user
@require_font
def glyphs_composition_get(request, font, *args, **kwargs):
    glyphs_composition_obj, _ = GlyphsComposition.objects.get_or_create(font_id=font.id)
    return ApiResponseSuccess(glyphs_composition_obj.serialize())


@api_view
@require_user
@require_font
@require_params(data='str')
def glyphs_composition_update(request, font, params, *args, **kwargs):
    glyphs_composition_data = params.get_dict('data')
    glyphs_composition_obj, _ = GlyphsComposition.objects.update_or_create(
        font_id=font.id, defaults={'data':glyphs_composition_data})
    return ApiResponseSuccess(glyphs_composition_obj.serialize())


@api_view
@require_user
@require_glif_filters
def glif_list(request, glif_filters, *args, **kwargs):
    data = {
        'atomic_elements': list(AtomicElement.objects.filter(**glif_filters).values(*ATOMIC_ELEMENT_ID_FIELDS)),
        'deep_components': list(DeepComponent.objects.filter(**glif_filters).values(*DEEP_COMPONENT_ID_FIELDS)),
        'character_glyphs': list(CharacterGlyph.objects.filter(**glif_filters).values(*CHARACTER_GLYPH_ID_FIELDS)),
    }
    return ApiResponseSuccess(data)


@api_view
@require_user
@require_glif_filters
def atomic_element_list(request, glif_filters, *args, **kwargs):
    data = list(AtomicElement.objects.filter(**glif_filters).values(*ATOMIC_ELEMENT_ID_FIELDS))
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
def atomic_element_create(request, user, font, data, glif, *args, **kwargs):
    filters = { 'font_id':font.id, 'name':glif.name }
    if AtomicElement.objects.filter(**filters).exists():
        return ApiResponseBadRequest(
            'Atomic Element with font_id=\'{}\' and name=\'{}\' already exists.'.format(font.id, glif.name))
    atomic_element = AtomicElement()
    atomic_element.font_id = font.id
    atomic_element.name = glif.name
    atomic_element.data = data
    atomic_element.lock_by(user)
    atomic_element.save_by(user)
    return ApiResponseSuccess(atomic_element.serialize())


@api_view
@require_user
@require_atomic_element(check_locked=True)
@require_data
def atomic_element_update(request, user, atomic_element, data, glif, *args, **kwargs):
    atomic_element.data = data
    atomic_element.save_by(user)
    return ApiResponseSuccess(atomic_element.serialize())


@api_view
@require_user
@require_atomic_element(check_locked=True)
@require_status
def atomic_element_update_status(request, user, atomic_element, status, *args, **kwargs):
    atomic_element.status = status
    atomic_element.save_by(user)
    return ApiResponseSuccess(atomic_element.serialize())


@api_view
@require_user
@require_atomic_element(check_locked=True)
def atomic_element_delete(request, atomic_element, *args, **kwargs):
    return ApiResponseSuccess(atomic_element.delete())


@api_view
@require_user
@require_atomic_element()
def atomic_element_lock(request, user, atomic_element, *args, **kwargs):
    if atomic_element.lock_by(user, save=True):
        return ApiResponseSuccess(atomic_element.serialize())
    return ApiResponseForbidden(
        'Atomic Element can\'t be locked, it has already been locked by another user.')


@api_view
@require_user
@require_atomic_element()
def atomic_element_unlock(request, user, atomic_element, *args, **kwargs):
    if atomic_element.unlock_by(user, save=True):
        return ApiResponseSuccess(atomic_element.serialize())
    return ApiResponseForbidden(
        'Atomic Element can\'t be unlocked, it has been locked by another user.')


@api_view
@require_user
@require_atomic_element(check_locked=True, prefix_params=True)
@require_data
@require_params(group_name='str')
def atomic_element_layer_create(request, user, params, font, atomic_element, data, glif, *args, **kwargs):
    group_name = params.get('group_name')
    options = {
        'glif_id': atomic_element.id,
        'group_name': group_name,
        'defaults': {
            'data': data,
            'updated_by': user,
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
@require_params(new_group_name='str')
def atomic_element_layer_rename(request, user, params, font, atomic_element, atomic_element_layer, *args, **kwargs):
    new_group_name = params.get('new_group_name')
    if AtomicElementLayer.objects.filter(glif_id=atomic_element.id, group_name__iexact=new_group_name).exclude(id=atomic_element_layer.id).exists():
        return ApiResponseBadRequest(
            'Atomic Element Layer with font_id=\'{}\', glif_id=\'{}\', glif__name=\'{}\', ' \
            'group_name=\'{}\' already exists, please choose a different group name.'.format(
                font.id, atomic_element.id, atomic_element.name, new_group_name))
    atomic_element_layer.group_name = new_group_name
    atomic_element_layer.save_by(user)
    return ApiResponseSuccess(atomic_element.serialize())


@api_view
@require_user
@require_atomic_element_layer()
@require_data
def atomic_element_layer_update(request, user, atomic_element, atomic_element_layer, data, *args, **kwargs):
    atomic_element_layer.data = data
    atomic_element_layer.save_by(user)
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
    data = list(DeepComponent.objects.filter(**glif_filters).values(*DEEP_COMPONENT_ID_FIELDS))
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
def deep_component_create(request, user, font, data, glif, *args, **kwargs):
    filters = { 'font_id':font.id, 'name':glif.name }
    if DeepComponent.objects.filter(**filters).exists():
        return ApiResponseBadRequest(
            'Deep Component with font_id=\'{}\' and name=\'{}\' already exists.'.format(font.id, glif.name))
    deep_component = DeepComponent()
    deep_component.font_id = font.id
    deep_component.name = glif.name
    deep_component.data = data
    deep_component.lock_by(user)
    deep_component.save_by(user)
    return ApiResponseSuccess(deep_component.serialize())


@api_view
@require_user
@require_deep_component(check_locked=True)
@require_data
def deep_component_update(request, user, deep_component, data, glif, *args, **kwargs):
    deep_component.data = data
    deep_component.save_by(user)
    return ApiResponseSuccess(deep_component.serialize())


@api_view
@require_user
@require_deep_component(check_locked=True)
@require_status
def deep_component_update_status(request, user, deep_component, status, *args, **kwargs):
    deep_component.status = status
    deep_component.save_by(user)
    return ApiResponseSuccess(deep_component.serialize())


@api_view
@require_user
@require_deep_component(check_locked=True)
def deep_component_delete(request, deep_component, *args, **kwargs):
    return ApiResponseSuccess(deep_component.delete())


@api_view
@require_user
@require_deep_component()
def deep_component_lock(request, user, deep_component, *args, **kwargs):
    if deep_component.lock_by(user, save=True):
        return ApiResponseSuccess(deep_component.serialize())
    return ApiResponseForbidden(
        'Deep Component can\'t be locked, it has already been locked by another user.')


@api_view
@require_user
@require_deep_component()
def deep_component_unlock(request, user, deep_component, *args, **kwargs):
    if deep_component.unlock_by(user, save=True):
        return ApiResponseSuccess(deep_component.serialize())
    return ApiResponseForbidden(
        'Deep Component can\'t be unlocked, it has been locked by another user.')


@api_view
@require_user
@require_glif_filters
def character_glyph_list(request, glif_filters, *args, **kwargs):
    data = list(CharacterGlyph.objects.filter(**glif_filters).values(*CHARACTER_GLYPH_ID_FIELDS))
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
def character_glyph_create(request, user, font, data, glif, *args, **kwargs):
    filters = { 'font_id':font.id, 'name':glif.name }
    if CharacterGlyph.objects.filter(**filters).exists():
        return ApiResponseBadRequest(
            'Character Glyph with font_id=\'{}\' and name=\'{}\' already exists.'.format(font.id, glif.name))
    character_glyph = CharacterGlyph()
    character_glyph.font_id = font.id
    character_glyph.name = glif.name
    character_glyph.data = data
    character_glyph.lock_by(user)
    character_glyph.save_by(user)
    return ApiResponseSuccess(character_glyph.serialize())


@api_view
@require_user
@require_character_glyph(check_locked=True)
@require_data
def character_glyph_update(request, user, character_glyph, data, glif, *args, **kwargs):
    # TODO: check lock
    character_glyph.data = data
    character_glyph.save_by(user)
    return ApiResponseSuccess(character_glyph.serialize())


@api_view
@require_user
@require_character_glyph(check_locked=True)
@require_status
def character_glyph_update_status(request, user, character_glyph, status, *args, **kwargs):
    character_glyph.status = status
    character_glyph.save_by(user)
    return ApiResponseSuccess(character_glyph.serialize())


@api_view
@require_user
@require_character_glyph(check_locked=True)
def character_glyph_delete(request, character_glyph, *args, **kwargs):
    return ApiResponseSuccess(character_glyph.delete())


@api_view
@require_user
@require_character_glyph()
def character_glyph_lock(request, user, character_glyph, *args, **kwargs):
    if character_glyph.lock_by(user, save=True):
        return ApiResponseSuccess(character_glyph.serialize())
    return ApiResponseForbidden(
        'Character Glyph can\'t be locked, it has already been locked by another user.')


@api_view
@require_user
@require_character_glyph()
def character_glyph_unlock(request, user, character_glyph, *args, **kwargs):
    if character_glyph.unlock_by(user, save=True):
        return ApiResponseSuccess(character_glyph.serialize())
    return ApiResponseForbidden(
        'Character Glyph can\'t be unlocked, it has been locked by another user.')


@api_view
@require_user
@require_character_glyph(check_locked=True, prefix_params=True)
@require_data
@require_params(group_name='str')
def character_glyph_layer_create(request, user, params, font, character_glyph, data, glif, *args, **kwargs):
    group_name = params.get('group_name')
    options = {
        'glif_id': character_glyph.id,
        'group_name': group_name,
        'defaults': {
            'data': data,
            'updated_by': user,
        },
    }
    layer, layer_created = CharacterGlyphLayer.objects.get_or_create(**options)
    if not layer_created:
        return ApiResponseBadRequest(
            'Character Glyph Layer with font_id=\'{}\', glif_id=\'{}\', glif__name=\'{}\', '
            'group_name=\'{}\' already exists.'.format(
                font.id, character_glyph.id, character_glyph.name, group_name))
    return ApiResponseSuccess(character_glyph.serialize())


@api_view
@require_user
@require_character_glyph_layer()
@require_params(new_group_name='str')
def character_glyph_layer_rename(request, user, params, font, character_glyph, character_glyph_layer, *args, **kwargs):
    new_group_name = params.get('new_group_name')
    if CharacterGlyphLayer.objects.filter(glif_id=character_glyph.id, group_name__iexact=new_group_name).exclude(id=character_glyph_layer.id).exists():
        return ApiResponseBadRequest(
            'Character Glyph Layer with font_id=\'{}\', glif_id=\'{}\', glif__name=\'{}\', ' \
            'group_name=\'{}\' already exists, please choose a different group name.'.format(
                font.id, character_glyph.id, character_glyph.name, new_group_name))
    character_glyph_layer.group_name = new_group_name
    character_glyph_layer.save_by(user)
    return ApiResponseSuccess(character_glyph.serialize())


@api_view
@require_user
@require_character_glyph_layer()
@require_data
def character_glyph_layer_update(request, user, character_glyph, character_glyph_layer, data, *args, **kwargs):
    character_glyph_layer.data = data
    character_glyph_layer.save_by(user)
    return ApiResponseSuccess(character_glyph.serialize())


@api_view
@require_user
@require_character_glyph_layer()
def character_glyph_layer_delete(request, character_glyph_layer, *args, **kwargs):
    return ApiResponseSuccess(character_glyph_layer.delete())

