from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Q

from robocjk.api.auth import get_auth_token
from robocjk.api.decorators import (
    api_view,
    require_atomic_element,
    require_atomic_element_layer,
    require_character_glyph,
    require_character_glyph_layer,
    require_data,
    require_deep_component,
    require_font,
    require_glif_filters,
    require_params,
    require_project,
    require_user,
)
from robocjk.api.http import (
    ApiResponseBadRequest,
    ApiResponseForbidden,
    ApiResponseSuccess,
)
from robocjk.api.serializers import (
    ATOMIC_ELEMENT_ID_FIELDS,
    CHARACTER_GLYPH_ID_FIELDS,
    DEEP_COMPONENT_ID_FIELDS,
    FONT_FIELDS,
    PROJECT_FIELDS,
    USER_FIELDS,
    serialize_user,
)
from robocjk.models import (
    AtomicElement,
    CharacterGlyph,
    DeepComponent,
    Font,
    GlyphsComposition,
    Project,
)
from robocjk.utils import unicodes_str_to_list
from robocjk.validators import GitSSHRepositoryURLValidator

UserClass = get_user_model()


@api_view
def ping(request, params, *args, **kwargs):
    return ApiResponseSuccess("pong")


@api_view
def auth_token(request, params, *args, **kwargs):
    username = params.get_str("username")
    password = params.get_str("password")
    if not username or not password:
        return ApiResponseBadRequest(
            "Unable to generate auth token, missing username and/or password parameters."
        )
    token_expiration = {"days": 1} if settings.DEBUG else {"minutes": 5}
    token = get_auth_token(request, username, password, expiration=token_expiration)
    if token is None:
        return ApiResponseBadRequest(
            "Unable to generate auth token, invalid credentials."
        )
    data = {
        "auth_token": token,
        "refresh_token": None,  # TODO
    }
    return ApiResponseSuccess(data)


def auth_refresh_token(request, *args, **kwargs):
    # TODO
    pass


@api_view
@require_user
def user_list(request, params, user, *args, **kwargs):
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
def project_list(request, params, user, *args, **kwargs):
    data = list(user.projects.values(*PROJECT_FIELDS))
    return ApiResponseSuccess(data)


@api_view
@require_user
@require_project
def project_get(request, params, user, project, *args, **kwargs):
    return ApiResponseSuccess(project.serialize())


@api_view
@require_user
@require_params(name="str", repo_url="str")
def project_create(request, params, user, *args, **kwargs):
    name = params.get_str("name")
    repo_url = params.get_str("repo_url")
    repo_branch = params.get_str("repo_branch", "master")
    try:
        repo_ssh_url_validator = GitSSHRepositoryURLValidator()
        repo_ssh_url_validator(repo_url)
    except ValidationError as repo_url_error:
        return ApiResponseBadRequest(
            "Invalid parameter 'repo_url': {} -> {}".format(
                repo_url, repo_url_error.message
            )
        )
    if Project.objects.filter(name__iexact=name).exists():
        return ApiResponseBadRequest(
            "Project with name='{}' already exists, "
            "please choose a different name.".format(name)
        )
    if Project.objects.filter(repo_url__iexact=repo_url).exists():
        return ApiResponseBadRequest(
            "Project with repo_url='{}' already exists, "
            "please choose a different repository url.".format(repo_url)
        )
    project = Project()
    project.name = name
    project.repo_url = repo_url
    project.repo_branch = repo_branch
    project.save_by(user)
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
def project_delete(request, params, user, project, *args, **kwargs):
    if not user.is_superuser:
        return ApiResponseForbidden("Only super-users are allowed to delete projects.")
    return ApiResponseSuccess(project.delete())


@api_view
@require_user
@require_project
def font_list(request, params, user, project, *args, **kwargs):
    font_fields = set(FONT_FIELDS)
    font_fields.remove("fontlib")
    font_fields.remove("designspace")
    font_fields = list(font_fields)
    data = list(project.fonts.values(*font_fields))
    return ApiResponseSuccess(data)


@api_view
@require_user
@require_font
def font_get(request, params, user, font, *args, **kwargs):
    return ApiResponseSuccess(font.serialize())


@api_view
@require_user
@require_project
@require_params(name="str")
def font_create(request, params, user, *args, **kwargs):
    project = kwargs["project"]
    name = params.get_str("name")
    if Font.objects.filter(name__iexact=name).exists():
        return ApiResponseBadRequest(
            "Font with name='{}' already exists, "
            "please choose a different name.".format(name)
        )
    font = Font()
    font.project = project
    font.name = name
    font.fontlib = params.get_dict("fontlib")
    font.features = params.get_str("features")
    font.designspace = params.get_dict("designspace")
    font.save_by(user)
    return ApiResponseSuccess(font.serialize())


@api_view
@require_user
@require_font
def font_update(request, params, user, font, *args, **kwargs):
    font_changed = False
    # look for fontlib data
    fontlib = params.get_dict("fontlib")
    if fontlib:
        font.fontlib = fontlib
        font_changed = True
    features = params.get_str("features")
    if features:
        font.features = features
        font_changed = True
    designspace = params.get_dict("designspace")
    if designspace:
        font.designspace = designspace
        font_changed = True
    # font is changed, save it
    if font_changed:
        font.save_by(user)
    return ApiResponseSuccess(font.serialize())


@api_view
@require_user
@require_font
def font_delete(request, params, user, font, *args, **kwargs):
    if not user.is_superuser:
        return ApiResponseForbidden("Only super-users are allowed to delete fonts.")
    return ApiResponseSuccess(font.delete())


@api_view
@require_user
@require_font
def glyphs_composition_get(request, params, user, font, *args, **kwargs):
    glyphs_composition_obj, _ = GlyphsComposition.objects.get_or_create(font_id=font.id)
    return ApiResponseSuccess(glyphs_composition_obj.serialize())


@api_view
@require_user
@require_font
@require_params(data="str")
def glyphs_composition_update(request, params, user, font, *args, **kwargs):
    glyphs_composition_data = params.get_dict("data")
    glyphs_composition_obj, _ = GlyphsComposition.objects.update_or_create(
        font_id=font.id, defaults={"data": glyphs_composition_data, "updated_by": user}
    )
    return ApiResponseSuccess(glyphs_composition_obj.serialize())


@api_view
@require_user
@require_font
@require_glif_filters
def glif_list(request, params, user, font, glif_filters, *args, **kwargs):
    updated_since = glif_filters.pop("updated_since", None)

    atomic_elements_qs = font.atomic_elements.filter(**glif_filters)
    deep_components_qs = font.deep_components.filter(**glif_filters)
    character_glyphs_qs = font.character_glyphs.filter(**glif_filters)

    if updated_since:
        atomic_elements_qs = atomic_elements_qs.filter(
            Q(updated_at__gt=updated_since) | Q(layers_updated_at__gt=updated_since)
        )
        deep_components_qs = deep_components_qs.filter(updated_at__gt=updated_since)
        character_glyphs_qs = character_glyphs_qs.filter(
            Q(updated_at__gt=updated_since) | Q(layers_updated_at__gt=updated_since)
        )

    atomic_elements_qs = atomic_elements_qs.values(*ATOMIC_ELEMENT_ID_FIELDS)
    atomic_elements_list = list(atomic_elements_qs)

    deep_components_qs = deep_components_qs.values(*DEEP_COMPONENT_ID_FIELDS)
    deep_components_list = list(deep_components_qs)

    character_glyphs_qs = character_glyphs_qs.values(*CHARACTER_GLYPH_ID_FIELDS)
    character_glyphs_list = list(character_glyphs_qs)

    # patch Character Glyphs data adding computed unicodes int list
    character_glyphs_count = len(character_glyphs_list)
    character_glyph_index = 0
    while character_glyph_index < character_glyphs_count:
        character_glyph_data = character_glyphs_list[character_glyph_index]
        character_glyph_unicode_hex = character_glyph_data.get("unicode_hex")
        if character_glyph_unicode_hex:
            character_glyph_data["unicodes"] = unicodes_str_to_list(
                character_glyph_unicode_hex,
                to_int=True,
            )
        character_glyph_index += 1

    data = {
        "atomic_elements": atomic_elements_list,
        "deep_components": deep_components_list,
        "character_glyphs": character_glyphs_list,
    }
    return ApiResponseSuccess(data)


@api_view
@require_user
@require_font
def glif_lock(request, params, user, font, *args, **kwargs):
    atomic_elements_ids = params.get_int_list("atomic_elements_ids")
    atomic_elements_names = params.get_str_list("atomic_elements_names")
    atomic_elements_list = []

    deep_components_ids = params.get_int_list("deep_components_ids")
    deep_components_names = params.get_str_list("deep_components_names")
    deep_components_list = []

    character_glyphs_ids = params.get_int_list("character_glyphs_ids")
    character_glyphs_names = params.get_str_list("character_glyphs_names")
    character_glyphs_list = []

    if atomic_elements_ids or atomic_elements_names:
        atomic_elements_qs = font.atomic_elements.filter(
            Q(id__in=atomic_elements_ids) | Q(name__in=atomic_elements_names)
        )
        atomic_elements_list = list(atomic_elements_qs)

    if deep_components_ids or deep_components_names:
        deep_components_qs = font.deep_components.filter(
            Q(id__in=deep_components_ids) | Q(name__in=deep_components_names)
        )
        deep_components_list = list(deep_components_qs)

    if character_glyphs_ids or character_glyphs_names:
        # fmt: off
        character_glyphs_qs = font.character_glyphs.filter(
            Q(id__in=character_glyphs_ids) |
            Q(name__in=character_glyphs_names) |
            Q(unicode_hex__in=character_glyphs_names)
        )
        # fmt: on
        character_glyphs_list = list(character_glyphs_qs)

    glif_list = atomic_elements_list + deep_components_list + character_glyphs_list
    for glif_obj in glif_list:
        glif_obj.lock_by(user, save=True)

    data = {
        "atomic_elements": list(
            [
                atomic_element_obj.serialize(options=params)
                for atomic_element_obj in atomic_elements_list
            ]
        ),
        "deep_components": list(
            [
                deep_components_obj.serialize(options=params)
                for deep_components_obj in deep_components_list
            ]
        ),
        "character_glyphs": list(
            [
                character_glyphs_obj.serialize(options=params)
                for character_glyphs_obj in character_glyphs_list
            ]
        ),
    }
    return ApiResponseSuccess(data)


@api_view
@require_user
@require_font
def glif_unlock(request, params, user, font, *args, **kwargs):
    atomic_elements_ids = params.get_int_list("atomic_elements_ids")
    atomic_elements_names = params.get_str_list("atomic_elements_names")
    atomic_elements_list = []

    deep_components_ids = params.get_int_list("deep_components_ids")
    deep_components_names = params.get_str_list("deep_components_names")
    deep_components_list = []

    character_glyphs_ids = params.get_int_list("character_glyphs_ids")
    character_glyphs_names = params.get_str_list("character_glyphs_names")
    character_glyphs_list = []

    if atomic_elements_ids or atomic_elements_names:
        atomic_elements_qs = font.atomic_elements.filter(
            Q(id__in=atomic_elements_ids) | Q(name__in=atomic_elements_names)
        )
        atomic_elements_list = list(atomic_elements_qs)

    if deep_components_ids or deep_components_names:
        deep_components_qs = font.deep_components.filter(
            Q(id__in=deep_components_ids) | Q(name__in=deep_components_names)
        )
        deep_components_list = list(deep_components_qs)

    if character_glyphs_ids or character_glyphs_names:
        # fmt: off
        character_glyphs_qs = font.character_glyphs.filter(
            Q(id__in=character_glyphs_ids) |
            Q(name__in=character_glyphs_names) |
            Q(unicode_hex__in=character_glyphs_names)
        )
        # fmt: on
        character_glyphs_list = list(character_glyphs_qs)

    glif_list = atomic_elements_list + deep_components_list + character_glyphs_list
    for glif_obj in glif_list:
        glif_obj.unlock_by(user, save=True)

    data = {
        "atomic_elements": list(
            [
                atomic_element_obj.serialize(options=params)
                for atomic_element_obj in atomic_elements_list
            ]
        ),
        "deep_components": list(
            [
                deep_components_obj.serialize(options=params)
                for deep_components_obj in deep_components_list
            ]
        ),
        "character_glyphs": list(
            [
                character_glyphs_obj.serialize(options=params)
                for character_glyphs_obj in character_glyphs_list
            ]
        ),
    }
    return ApiResponseSuccess(data)


@api_view
@require_user
@require_font
@require_glif_filters
def atomic_element_list(request, params, user, font, glif_filters, *args, **kwargs):
    data = list(
        font.atomic_elements.filter(**glif_filters).values(*ATOMIC_ELEMENT_ID_FIELDS)
    )
    return ApiResponseSuccess(data)


@api_view
@require_user
@require_atomic_element()
def atomic_element_get(request, params, user, atomic_element, *args, **kwargs):
    return ApiResponseSuccess(atomic_element.serialize(options=params))


@api_view
@require_user
@require_font
@require_data
def atomic_element_create(request, params, user, font, data, glif, *args, **kwargs):
    if font.atomic_elements.filter(name=glif.name).exists():
        return ApiResponseBadRequest(
            "Atomic Element with font_uid='{}' and name='{}' already exists.".format(
                font.uid, glif.name
            )
        )
    atomic_element = AtomicElement()
    atomic_element.font_id = font.id
    atomic_element.name = glif.name
    atomic_element.data = data
    # atomic_element.lock_by(user)
    atomic_element.save_by(user)
    return ApiResponseSuccess(atomic_element.serialize(options=params))


@api_view
@require_user
@require_atomic_element(check_locked=True)
@require_data
def atomic_element_update(
    request, params, user, atomic_element, data, glif, *args, **kwargs
):
    atomic_element.data = data
    atomic_element.save_by(user)
    return ApiResponseSuccess(atomic_element.serialize(options=params))


@api_view
@require_user
@require_atomic_element(check_locked=True)
def atomic_element_delete(request, params, user, atomic_element, *args, **kwargs):
    return ApiResponseSuccess(atomic_element.delete())


@api_view
@require_user
@require_atomic_element()
def atomic_element_lock(request, params, user, atomic_element, *args, **kwargs):
    if atomic_element.lock_by(user, save=True):
        return ApiResponseSuccess(atomic_element.serialize(options=params))
    return ApiResponseForbidden(
        "Atomic Element can't be locked, it has already been locked by another user."
    )


@api_view
@require_user
@require_atomic_element()
def atomic_element_unlock(request, params, user, atomic_element, *args, **kwargs):
    if atomic_element.unlock_by(user, save=True):
        return ApiResponseSuccess(atomic_element.serialize(options=params))
    return ApiResponseForbidden(
        "Atomic Element can't be unlocked, it has been locked by another user."
    )


@api_view
@require_user
@require_atomic_element(check_locked=True, prefix_params=True)
@require_data
@require_params(group_name="str")
def atomic_element_layer_create(
    request, params, user, font, atomic_element, data, glif, *args, **kwargs
):
    group_name = params.get("group_name")
    options = {
        "glif_id": atomic_element.id,
        "group_name": group_name,
        "defaults": {
            "data": data,
            "updated_by": user,
        },
    }
    layer, layer_created = atomic_element.layers.get_or_create(**options)
    if not layer_created:
        return ApiResponseBadRequest(
            "Atomic Element Layer with font_uid='{}', glif_id='{}', "
            "glif__name='{}' group_name='{}' already exists.".format(
                font.uid, atomic_element.id, atomic_element.name, group_name
            )
        )
    return ApiResponseSuccess(atomic_element.serialize(options=params))


@api_view
@require_user
@require_atomic_element_layer()
@require_params(new_group_name="str")
def atomic_element_layer_rename(
    request, params, user, font, atomic_element, atomic_element_layer, *args, **kwargs
):
    new_group_name = params.get("new_group_name")
    if (
        atomic_element.layers.filter(group_name__iexact=new_group_name)
        .exclude(id=atomic_element_layer.id)
        .exists()
    ):
        return ApiResponseBadRequest(
            "Atomic Element Layer with font_uid='{}', glif_id='{}', glif__name='{}', "
            "group_name='{}' already exists, please choose a different group name.".format(
                font.uid, atomic_element.id, atomic_element.name, new_group_name
            )
        )
    atomic_element_layer.group_name = new_group_name
    atomic_element_layer.save_by(user)
    return ApiResponseSuccess(atomic_element.serialize(options=params))


@api_view
@require_user
@require_atomic_element_layer()
@require_data
def atomic_element_layer_update(
    request, params, user, atomic_element, atomic_element_layer, data, *args, **kwargs
):
    atomic_element_layer.data = data
    atomic_element_layer.save_by(user)
    return ApiResponseSuccess(atomic_element.serialize(options=params))


@api_view
@require_user
@require_atomic_element_layer()
def atomic_element_layer_delete(
    request, params, user, atomic_element_layer, *args, **kwargs
):
    return ApiResponseSuccess(atomic_element_layer.delete())


@api_view
@require_user
@require_font
@require_glif_filters
def deep_component_list(request, params, user, font, glif_filters, *args, **kwargs):
    data = list(
        font.deep_components.filter(**glif_filters).values(*DEEP_COMPONENT_ID_FIELDS)
    )
    return ApiResponseSuccess(data)


@api_view
@require_user
@require_deep_component()
def deep_component_get(request, params, user, deep_component, *args, **kwargs):
    return ApiResponseSuccess(deep_component.serialize(options=params))


@api_view
@require_user
@require_font
@require_data
def deep_component_create(request, params, user, font, data, glif, *args, **kwargs):
    if font.deep_components.filter(name=glif.name).exists():
        return ApiResponseBadRequest(
            "Deep Component with font_uid='{}' and name='{}' already exists.".format(
                font.uid, glif.name
            )
        )
    deep_component = DeepComponent()
    deep_component.font_id = font.id
    deep_component.name = glif.name
    deep_component.data = data
    # deep_component.lock_by(user)
    deep_component.save_by(user)
    return ApiResponseSuccess(deep_component.serialize(options=params))


@api_view
@require_user
@require_deep_component(check_locked=True)
@require_data
def deep_component_update(
    request, params, user, deep_component, data, glif, *args, **kwargs
):
    deep_component.data = data
    deep_component.save_by(user)
    return ApiResponseSuccess(deep_component.serialize(options=params))


@api_view
@require_user
@require_deep_component(check_locked=True)
def deep_component_delete(request, params, user, deep_component, *args, **kwargs):
    return ApiResponseSuccess(deep_component.delete())


@api_view
@require_user
@require_deep_component()
def deep_component_lock(request, params, user, deep_component, *args, **kwargs):
    if deep_component.lock_by(user, save=True):
        return ApiResponseSuccess(deep_component.serialize(options=params))
    return ApiResponseForbidden(
        "Deep Component can't be locked, it has already been locked by another user."
    )


@api_view
@require_user
@require_deep_component()
def deep_component_unlock(request, params, user, deep_component, *args, **kwargs):
    if deep_component.unlock_by(user, save=True):
        return ApiResponseSuccess(deep_component.serialize(options=params))
    return ApiResponseForbidden(
        "Deep Component can't be unlocked, it has been locked by another user."
    )


@api_view
@require_user
@require_font
@require_glif_filters
def character_glyph_list(request, params, user, font, glif_filters, *args, **kwargs):
    data = list(
        font.character_glyphs.filter(**glif_filters).values(*CHARACTER_GLYPH_ID_FIELDS)
    )
    return ApiResponseSuccess(data)


@api_view
@require_user
@require_character_glyph()
def character_glyph_get(request, params, user, character_glyph, *args, **kwargs):
    return ApiResponseSuccess(character_glyph.serialize(options=params))


@api_view
@require_user
@require_font
@require_data
def character_glyph_create(request, params, user, font, data, glif, *args, **kwargs):
    if font.character_glyphs.filter(name=glif.name).exists():
        return ApiResponseBadRequest(
            "Character Glyph with font_uid='{}' and name='{}' already exists.".format(
                font.uid, glif.name
            )
        )
    character_glyph = CharacterGlyph()
    character_glyph.font_id = font.id
    character_glyph.name = glif.name
    character_glyph.data = data
    # character_glyph.lock_by(user)
    character_glyph.save_by(user)
    return ApiResponseSuccess(character_glyph.serialize(options=params))


@api_view
@require_user
@require_character_glyph(check_locked=True)
@require_data
def character_glyph_update(
    request, params, user, character_glyph, data, glif, *args, **kwargs
):
    character_glyph.data = data
    character_glyph.save_by(user)
    return ApiResponseSuccess(character_glyph.serialize(options=params))


@api_view
@require_user
@require_character_glyph(check_locked=True)
def character_glyph_delete(request, params, user, character_glyph, *args, **kwargs):
    return ApiResponseSuccess(character_glyph.delete())


@api_view
@require_user
@require_character_glyph()
def character_glyph_lock(request, params, user, character_glyph, *args, **kwargs):
    if character_glyph.lock_by(user, save=True):
        return ApiResponseSuccess(character_glyph.serialize(options=params))
    return ApiResponseForbidden(
        "Character Glyph can't be locked, it has already been locked by another user."
    )


@api_view
@require_user
@require_character_glyph()
def character_glyph_unlock(request, params, user, character_glyph, *args, **kwargs):
    if character_glyph.unlock_by(user, save=True):
        return ApiResponseSuccess(character_glyph.serialize(options=params))
    return ApiResponseForbidden(
        "Character Glyph can't be unlocked, it has been locked by another user."
    )


@api_view
@require_user
@require_character_glyph(check_locked=True, prefix_params=True)
@require_data
@require_params(group_name="str")
def character_glyph_layer_create(
    request, params, user, font, character_glyph, data, glif, *args, **kwargs
):
    group_name = params.get("group_name")
    options = {
        "glif_id": character_glyph.id,
        "group_name": group_name,
        "defaults": {
            "data": data,
            "updated_by": user,
        },
    }
    layer, layer_created = character_glyph.layers.get_or_create(**options)
    if not layer_created:
        return ApiResponseBadRequest(
            "Character Glyph Layer with font_uid='{}', glif_id='{}', glif__name='{}', "
            "group_name='{}' already exists.".format(
                font.uid, character_glyph.id, character_glyph.name, group_name
            )
        )
    return ApiResponseSuccess(character_glyph.serialize(options=params))


@api_view
@require_user
@require_character_glyph_layer()
@require_params(new_group_name="str")
def character_glyph_layer_rename(
    request, params, user, font, character_glyph, character_glyph_layer, *args, **kwargs
):
    new_group_name = params.get("new_group_name")
    if (
        character_glyph.layers.filter(group_name__iexact=new_group_name)
        .exclude(id=character_glyph_layer.id)
        .exists()
    ):
        return ApiResponseBadRequest(
            "Character Glyph Layer with font_uid='{}', glif_id='{}', glif__name='{}', "
            "group_name='{}' already exists, please choose a different group name.".format(
                font.uid, character_glyph.id, character_glyph.name, new_group_name
            )
        )
    character_glyph_layer.group_name = new_group_name
    character_glyph_layer.save_by(user)
    return ApiResponseSuccess(character_glyph.serialize(options=params))


@api_view
@require_user
@require_character_glyph_layer()
@require_data
def character_glyph_layer_update(
    request, params, user, character_glyph, character_glyph_layer, data, *args, **kwargs
):
    character_glyph_layer.data = data
    character_glyph_layer.save_by(user)
    return ApiResponseSuccess(character_glyph.serialize(options=params))


@api_view
@require_user
@require_character_glyph_layer()
def character_glyph_layer_delete(
    request, params, user, character_glyph_layer, *args, **kwargs
):
    return ApiResponseSuccess(character_glyph_layer.delete())
