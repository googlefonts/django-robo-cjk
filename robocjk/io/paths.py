import re
from urllib.parse import unquote

import fsutil
from django.conf import settings

FONT_PATTERN = r"((?P<font_name>[\w\-_\.]+)\.rcjk\/)"
FONTLIB_PATTERN = r"^{}?fontLib\.json$".format(FONT_PATTERN)
FEATURES_PATTERN = r"^{}?features\.fea$".format(FONT_PATTERN)
DESIGNSPACE_PATTERN = r"^{}?designspace\.json$".format(FONT_PATTERN)
NAME_PATTERN = r"[\w\-\_\.\+\(\)\[\]]+"
ATOMIC_ELEMENT_PATTERN = r"^{}?atomicElement\/(?P<glif_name>{})\.glif$".format(
    FONT_PATTERN, NAME_PATTERN
)
ATOMIC_ELEMENT_LAYER_PATTERN = (
    r"^{}?atomicElement\/(?P<layer_name>{})\/(?P<glif_name>{})\.glif$".format(
        FONT_PATTERN, NAME_PATTERN, NAME_PATTERN
    )
)
DEEP_COMPONENT_PATTERN = r"^{}?deepComponent\/(?P<glif_name>{})\.glif$".format(
    FONT_PATTERN, NAME_PATTERN
)
CHARACTER_GLYPH_PATTERN = r"^{}?characterGlyph\/(?P<glif_name>{})\.glif$".format(
    FONT_PATTERN, NAME_PATTERN
)
CHARACTER_GLYPH_LAYER_PATTERN = (
    r"^{}?characterGlyph\/(?P<layer_name>{})\/(?P<glif_name>{})\.glif$".format(
        FONT_PATTERN, NAME_PATTERN, NAME_PATTERN
    )
)

FONT_RE = re.compile(FONT_PATTERN)
FONTLIB_RE = re.compile(FONTLIB_PATTERN)
FEATURES_RE = re.compile(FEATURES_PATTERN)
DESIGNSPACE_RE = re.compile(DESIGNSPACE_PATTERN)
ATOMIC_ELEMENT_RE = re.compile(ATOMIC_ELEMENT_PATTERN)
ATOMIC_ELEMENT_LAYER_RE = re.compile(ATOMIC_ELEMENT_LAYER_PATTERN)
DEEP_COMPONENT_RE = re.compile(DEEP_COMPONENT_PATTERN)
CHARACTER_GLYPH_RE = re.compile(CHARACTER_GLYPH_PATTERN)
CHARACTER_GLYPH_LAYER_RE = re.compile(CHARACTER_GLYPH_LAYER_PATTERN)


def quote_filename(filename):
    unsafe_table = {
        ord("%"): "%25",
        ord("/"): "%2F",
        ord("\\"): "%5C",
    }
    return filename.translate(unsafe_table)


def unquote_filename(filename):
    return unquote(filename)


def get_project_path(instance, name=None):
    project_name = quote_filename(name or instance.slug)
    return fsutil.join_path(
        settings.GIT_REPOSITORIES_PATH,
        project_name,
    )


def get_font_path(instance, name=None):
    font_name = quote_filename(name or instance.slug)
    return fsutil.join_path(
        get_project_path(instance.project),
        "{}.rcjk".format(font_name),
    )


def get_glif_filename(instance, name=None):
    filename = quote_filename(name or instance.filename)
    assert filename.endswith(".glif")
    return filename


def get_character_glyphs_path(font):
    return fsutil.join_path(
        get_font_path(font),
        "characterGlyph",
    )


def get_character_glyph_path(instance, name=None):
    return fsutil.join_path(
        get_character_glyphs_path(instance.font),
        get_glif_filename(instance, name),
    )


def get_character_glyph_layer_path(instance, name=None):
    layer_group_name = quote_filename(instance.group_name)
    return fsutil.join_path(
        get_character_glyphs_path(instance.glif.font),
        layer_group_name,
        get_glif_filename(instance, name),
    )


def get_deep_components_path(font):
    return fsutil.join_path(
        get_font_path(font),
        "deepComponent",
    )


def get_deep_component_path(instance, name=None):
    return fsutil.join_path(
        get_deep_components_path(instance.font),
        get_glif_filename(instance, name),
    )


def get_atomic_elements_path(font):
    return fsutil.join_path(
        get_font_path(font),
        "atomicElement",
    )


def get_atomic_element_path(instance, name=None):
    return fsutil.join_path(
        get_atomic_elements_path(instance.font),
        get_glif_filename(instance, name),
    )


def get_atomic_element_layer_path(instance, name=None):
    layer_group_name = quote_filename(instance.group_name)
    return fsutil.join_path(
        get_atomic_elements_path(instance.glif.font),
        layer_group_name,
        get_glif_filename(instance, name),
    )


def get_proof_path(instance):
    return fsutil.join_path(
        get_font_path(instance.font),
        "Proofing",
        fsutil.get_filename(instance.file.path),
    )
