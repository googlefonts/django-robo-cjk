# -*- coding: utf-8 -*-

from benedict import benedict

from robocjk.models import (
    Project, Font, CharacterGlyph, CharacterGlyphLayer, DeepComponent,
    AtomicElement, AtomicElementLayer, Proof, )


def _get_glif_fields():
    return [
        'id', 'data', 'name', 'filename', 'unicode_hex',
        'is_locked', 'locked_by', 'locked_at', 'status',
        'is_empty', 'has_variation_axis', 'has_outlines', 'has_components', 'has_unicode',
    ]

def _get_glif_layer_fields():
    return [
        'id', 'data', 'group_name', 'name', 'filename',
        'is_empty', 'has_variation_axis', 'has_outlines', 'has_components', 'has_unicode',
    ]

def _get_ref_glif_fields():
    return [
        'id', 'name',
    ]


def get_atomic_elements(filters=None, fields=None):
    filters = filters or {}
    fields = fields or ['id', 'name']
    return list(AtomicElement.objects.filter(**filters).values(*fields))


def get_deep_components(filters=None, fields=None):
    filters = filters or {}
    fields = fields or ['id', 'name']
    return list(DeepComponent.objects.filter(**filters).values(*fields))


def get_character_glyphs(filters=None, fields=None):
    filters = filters or {}
    fields = fields or ['id', 'name', 'unicode_hex']
    return list(CharacterGlyph.objects.filter(**filters).values(*fields))


def get_atomic_element(filters):
    fields = _get_glif_fields()
    layer_fields = _get_glif_layer_fields()
    try:
        obj = AtomicElement.objects.prefetch_related('layers').get(**filters)
    except AtomicElement.DoesNotExist:
        # TODO: log
        return None
    except AtomicElement.MultipleObjectsReturned:
        # TODO: log
        return None
    else:
        data = { field:getattr(obj, field, None) for field in fields }
        data['type'] = 'Atomic Element'
        data['type_code'] = 'AE'
        data['made_of'] = []
        data['used_by'] = list(obj.deep_components.all().values(*['id', 'name']))
        data['layers'] = list(obj.layers.all().values(*layer_fields))
        return data


def get_deep_component(filters):
    fields = _get_glif_fields()
    try:
        obj = DeepComponent.objects.prefetch_related('atomic_elements', 'character_glyphs').get(**filters)
    except DeepComponent.DoesNotExist:
        # TODO: log
        return None
    except DeepComponent.MultipleObjectsReturned:
        # TODO: log
        return None
    else:
        data = { field:getattr(obj, field, None) for field in fields }
        data['type'] = 'Deep Component'
        data['type_code'] = 'DC'
        data['made_of'] = list(obj.atomic_elements.values(*fields))
        data['used_by'] = list(obj.character_glyphs.all().values(*['id', 'name', 'unicode_hex']))
        data['layers'] = []
        return data


def get_character_glyph(filters):
    fields = _get_glif_fields()
    layer_fields = _get_glif_layer_fields()
    try:
        obj = CharacterGlyph.objects.prefetch_related('deep_components', 'layers').get(**filters)
    except CharacterGlyph.DoesNotExist:
        # TODO: log
        return None
    except CharacterGlyph.MultipleObjectsReturned:
        # TODO: log
        return None
    else:
        data = { field:getattr(obj, field, None) for field in fields }
        data['type'] = 'Character Glyph'
        data['type_code'] = 'CG'
        data['made_of'] = list(obj.deep_components.values(*fields))
        data['used_by'] = []
        data['layers'] = list(obj.layers.all().values(*layer_fields))
        return data

