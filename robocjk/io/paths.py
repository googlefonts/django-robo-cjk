# -*- coding: utf-8 -*-

from fileutil import fileutil

from robocjk.io import settings as io_settings

import os


def get_project_path(instance, name=None):
    return os.path.join(
        io_settings.GIT_REPOSITORIES_PATH,
        (name or instance.slug))


def get_font_path(instance, name=None):
    return os.path.join(
        get_project_path(instance.project),
        '{}.rcjk'.format(name or instance.slug))


def get_glif_filename(instance, name=None):
    filename = name or instance.filename
    assert filename.endswith('.glif')
    return filename


def get_character_glyph_path(instance, name=None):
    return os.path.join(
        get_font_path(instance.font),
        'characterGlyph',
        get_glif_filename(instance, name))


def get_character_glyph_layer_path(instance, name=None):
    return os.path.join(
        get_font_path(instance.glif.font),
        'characterGlyph',
        instance.group_name,
        get_glif_filename(instance, name))


def get_deep_component_path(instance, name=None):
    return os.path.join(
        get_font_path(instance.font),
        'deepComponent',
        get_glif_filename(instance, name))


def get_atomic_element_path(instance, name=None):
    return os.path.join(
        get_font_path(instance.font),
        'atomicElement',
        get_glif_filename(instance, name))


def get_atomic_element_layer_path(instance, name=None):
    return os.path.join(
        get_font_path(instance.glif.font),
        'atomicElement',
        instance.group_name,
        get_glif_filename(instance, name))


def get_proof_path(instance):
    return os.path.join(
        get_font_path(instance.font),
        'Proofing',
        fileutil.get_filename(self.file.path))
