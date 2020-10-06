# -*- coding: utf-8 -*-


GLIF_FIELDS = [
    'id', 'data', 'name', 'filename', 'unicode_hex',
    'is_locked', 'locked_by_id', 'locked_at', 'status',
    'is_empty', 'has_variation_axis', 'has_outlines', 'has_components', 'has_unicode',
]

GLIF_LAYER_FIELDS = [
    'glif_id', 'id', 'data', 'group_name', 'name', 'filename',
    'is_empty', 'has_variation_axis', 'has_outlines', 'has_components', 'has_unicode',
]


def _serialize_object(obj, fields):
    return { field:getattr(obj, field, None) for field in fields }


def _serialize_glif(obj):
    data = _serialize_object(obj, GLIF_FIELDS)
    data['locked_by_user'] = None
    if obj.locked_by_id:
        user = obj.locked_by
        data['locked_by_user'] = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
    return data


def _serialize_glif_layer(obj):
    data = _serialize_object(obj, GLIF_LAYER_FIELDS)
    return data


def serialize_atomic_element(obj, **kwargs):
    data = _serialize_glif(obj)
    data['type'] = 'Atomic Element'
    data['type_code'] = 'AE'
    data['made_of'] = []
    data['used_by'] = list(obj.deep_components.values(*['id', 'name']))
    data['layers'] = list(obj.layers.values(*GLIF_LAYER_FIELDS))
    return data


def serialize_atomic_element_layer(obj, **kwargs):
    return _serialize_glif_layer(obj)


def serialize_deep_component(obj, **kwargs):
    data = _serialize_glif(obj)
    data['type'] = 'Deep Component'
    data['type_code'] = 'DC'
    data['made_of'] = list(obj.atomic_elements.values(*GLIF_FIELDS))
    data['used_by'] = list(obj.character_glyphs.values(*['id', 'name', 'unicode_hex']))
    data['layers'] = []
    return data


def serialize_character_glyph(obj, **kwargs):
    data = _serialize_glif(obj)
    data['type'] = 'Character Glyph'
    data['type_code'] = 'CG'
    data['made_of'] = list(obj.deep_components.values(*GLIF_FIELDS))
    data['used_by'] = []
    data['layers'] = list(obj.layers.values(*GLIF_LAYER_FIELDS))
    return data


def serialize_character_glyph_layer(obj, **kwargs):
    return _serialize_glif_layer(obj)

