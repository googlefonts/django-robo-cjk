# -*- coding: utf-8 -*-

import re


FONT_PATTERN = r'((?P<font_name>[\w\-_\.]+)\.rcjk\/)'
FONTLIB_PATTERN = r'^{}?fontLib\.json$'.format(FONT_PATTERN)
FEATURES_PATTERN = r'^{}?features\.fea$'.format(FONT_PATTERN)
DESIGNSPACE_PATTERN = r'^{}?designspace\.json$'.format(FONT_PATTERN)
ATOMIC_ELEMENT_PATTERN = r'^{}?atomicElement\/(?P<glif_name>[\w\-\_\.\+]+)\.glif$'.format(FONT_PATTERN)
ATOMIC_ELEMENT_LAYER_PATTERN = r'^{}?atomicElement\/(?P<layer_name>[\w\-\_\.\+]+)\/(?P<glif_name>[\w\-\_\.\+]+)\.glif$'.format(FONT_PATTERN)
DEEP_COMPONENT_PATTERN = r'^{}?deepComponent\/(?P<glif_name>[\w\-\_\.\+]+)\.glif$'.format(FONT_PATTERN)
CHARACTER_GLYPH_PATTERN = r'^{}?characterGlyph\/(?P<glif_name>[\w\-\_\.\+]+)\.glif$'.format(FONT_PATTERN)
CHARACTER_GLYPH_LAYER_PATTERN = r'^{}?characterGlyph\/(?P<layer_name>[\w\-\_\.\+]+)\/(?P<glif_name>[\w\-\_\.\+]+)\.glif$'.format(FONT_PATTERN)

FONT_RE = re.compile(FONT_PATTERN)
FONTLIB_RE = re.compile(FONTLIB_PATTERN)
FEATURES_RE = re.compile(FEATURES_PATTERN)
DESIGNSPACE_RE = re.compile(DESIGNSPACE_PATTERN)
ATOMIC_ELEMENT_RE = re.compile(ATOMIC_ELEMENT_PATTERN)
ATOMIC_ELEMENT_LAYER_RE = re.compile(ATOMIC_ELEMENT_LAYER_PATTERN)
DEEP_COMPONENT_RE = re.compile(DEEP_COMPONENT_PATTERN)
CHARACTER_GLYPH_RE = re.compile(CHARACTER_GLYPH_PATTERN)
CHARACTER_GLYPH_LAYER_RE = re.compile(CHARACTER_GLYPH_LAYER_PATTERN)

# git log --since="60 minutes ago" --name-only | sort | uniq