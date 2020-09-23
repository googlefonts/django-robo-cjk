# -*- coding: utf-8 -*-

from .models import (
    Project, Font, CharacterGlyph, CharacterGlyphLayer, DeepComponent,
    AtomicElement, AtomicElementLayer, Proof, )



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
    fields = [
        'id', 'name', 'filename', 'unicode_hex', 'data',
        'is_locked', 'locked_by', 'locked_at', 'status',
        'is_empty', 'has_variation_axis', 'has_outlines', 'has_components', 'has_unicode',
    ]
    data = list(AtomicElement.objects.filter(**filters).values(*fields))
    # TODO: add in_deep_components: []
    return data
