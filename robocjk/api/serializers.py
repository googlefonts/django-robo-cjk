# -*- coding: utf-8 -*-


USER_FIELDS = [
    'id', 'username', 'first_name', 'last_name', 'email',
]

PROJECT_FIELDS = [
    'uid', 'name', 'slug', 'repo_url', 'repo_branch',
]

FONT_FIELDS = [
    'uid', 'name', 'slug', 'available', 'fontlib', 'features', 'designspace',
]

ATOMIC_ELEMENT_ID_FIELDS = [
    'id', 'name',
]
DEEP_COMPONENT_ID_FIELDS = [
    'id', 'name',
]
CHARACTER_GLYPH_ID_FIELDS = [
    'id', 'name', 'unicode_hex',
]

GLIF_FIELDS = [
    'id', 'data', 'name', 'filename', 'unicode_hex',
    'is_locked', 'locked_by_id', 'locked_at', 'status',
    'is_empty', 'has_variation_axis', 'has_outlines', 'has_components', 'has_unicode',
    'created_at', 'updated_at',
]

GLIF_LAYER_FIELDS = [
    'glif_id', 'id', 'data', 'group_name', 'name', 'filename',
    'is_empty', 'has_variation_axis', 'has_outlines', 'has_components', 'has_unicode',
    'created_at', 'updated_at',
]


def _serialize_object(obj, fields, **kwargs):
    exclude_fields = kwargs.get('exclude_fields', [])
    return { field:getattr(obj, field, None) for field in fields if not field in exclude_fields }


def serialize_user(obj, **kwargs):
    data = _serialize_object(obj, USER_FIELDS, **kwargs)
    return data


def serialize_project(obj, **kwargs):
    data = _serialize_object(obj, PROJECT_FIELDS, **kwargs)
#     return_related = kwargs.get('return_related', True)
#     if return_related:
#         data['designers'] = [serialize_user(user_obj, **kwargs) for user_obj in obj.designers.all()]
    return data


def serialize_font(obj, **kwargs):
    data = _serialize_object(obj, FONT_FIELDS, **kwargs)
    return data


def _serialize_glif(obj, **kwargs):
    data = _serialize_object(obj, GLIF_FIELDS, **kwargs)
    data['locked_by_user'] = None
    if obj.locked_by_id:
        user = obj.locked_by
        data['locked_by_user'] = serialize_user(user, **kwargs)
    return data


def _serialize_glif_layer(obj, **kwargs):
    data = _serialize_object(obj, GLIF_LAYER_FIELDS, **kwargs)
    return data


def serialize_atomic_element(obj, **kwargs):
    return_layers = kwargs.get('return_layers', True)
    return_related = kwargs.get('return_related', True)
    data = _serialize_glif(obj, **kwargs)
    data['type'] = 'Atomic Element'
    data['type_code'] = 'AE'
    if return_layers:
        data['layers'] = list(obj.layers.values(*GLIF_LAYER_FIELDS))
    if return_related:
        data['made_of'] = []
        data['used_by'] = list(obj.deep_components.values(*DEEP_COMPONENT_ID_FIELDS))
    return data


def serialize_atomic_element_layer(obj, **kwargs):
    return _serialize_glif_layer(obj)


def serialize_deep_component(obj, **kwargs):
    return_layers = kwargs.get('return_layers', True)
    return_related = kwargs.get('return_related', True)
    data = _serialize_glif(obj, **kwargs)
    data['type'] = 'Deep Component'
    data['type_code'] = 'DC'
    if return_layers:
        data['layers'] = []
    if return_related:
        data['made_of'] = list([
            serialize_atomic_element(glif_obj, **kwargs) for glif_obj in obj.atomic_elements.all()
        ])
        data['used_by'] = list(obj.character_glyphs.values(*CHARACTER_GLYPH_ID_FIELDS))
    return data


def serialize_character_glyph(obj, **kwargs):
    return_layers = kwargs.get('return_layers', True)
    return_related = kwargs.get('return_related', True)
    data = _serialize_glif(obj, **kwargs)
    data['type'] = 'Character Glyph'
    data['type_code'] = 'CG'
    if return_layers:
        data['layers'] = list(obj.layers.values(*GLIF_LAYER_FIELDS))
    if return_related:
        made_of_character_glyphs = []
        # create a set for storing character-glyphs ids to avoid possible circular references
        made_of_character_glyphs_refs = kwargs.get('made_of_character_glyphs_refs', set())
        if obj.id not in made_of_character_glyphs_refs:
            made_of_character_glyphs_refs.add(obj.id)
            kwargs['made_of_character_glyphs_refs'] = made_of_character_glyphs_refs
            made_of_character_glyphs = list([
                serialize_character_glyph(glif_obj, **kwargs) for glif_obj in obj.character_glyphs.all()
            ])
        made_of_deep_components = list([
            serialize_deep_component(glif_obj, **kwargs) for glif_obj in obj.deep_components.all()
        ])
        data['made_of'] = made_of_character_glyphs + made_of_deep_components
        used_by_character_glyphs = list(obj.used_by_character_glyphs.values(*CHARACTER_GLYPH_ID_FIELDS))
        data['used_by'] = used_by_character_glyphs
    return data


def serialize_character_glyph_layer(obj, **kwargs):
    return _serialize_glif_layer(obj)

