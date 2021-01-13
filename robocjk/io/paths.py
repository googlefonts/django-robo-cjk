# -*- coding: utf-8 -*-

from robocjk.settings import GIT_REPOSITORIES_PATH

import fsutil


def get_project_path(instance, name=None):
    return fsutil.join_path(
        GIT_REPOSITORIES_PATH,
        (name or instance.slug))


def get_font_path(instance, name=None):
    return fsutil.join_path(
        get_project_path(instance.project),
        '{}.rcjk'.format(name or instance.slug))


def get_glif_filename(instance, name=None):
    filename = name or instance.filename
    assert filename.endswith('.glif')
    return filename


def get_character_glyphs_path(font):
    return fsutil.join_path(
        get_font_path(font), 'characterGlyph')


def get_character_glyph_path(instance, name=None):
    return fsutil.join_path(
        get_character_glyphs_path(instance.font),
        get_glif_filename(instance, name))


def get_character_glyph_layer_path(instance, name=None):
    return fsutil.join_path(
        get_character_glyphs_path(instance.glif.font),
        instance.group_name,
        get_glif_filename(instance, name))


def get_deep_components_path(font):
    return fsutil.join_path(
        get_font_path(font), 'deepComponent')


def get_deep_component_path(instance, name=None):
    return fsutil.join_path(
        get_deep_components_path(instance.font),
        get_glif_filename(instance, name))


def get_atomic_elements_path(font):
    return fsutil.join_path(
        get_font_path(font), 'atomicElement')


def get_atomic_element_path(instance, name=None):
    return fsutil.join_path(
        get_atomic_elements_path(instance.font),
        get_glif_filename(instance, name))


def get_atomic_element_layer_path(instance, name=None):
    return fsutil.join_path(
        get_atomic_elements_path(instance.glif.font),
        instance.group_name,
        get_glif_filename(instance, name))


def get_proof_path(instance):
    return fsutil.join_path(
        get_font_path(instance.font),
        'Proofing',
        fsutil.get_filename(self.file.path))
