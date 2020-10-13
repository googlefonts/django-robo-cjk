# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from robocjk.core import GlifData
from robocjk.models import (
    Project, Font, CharacterGlyph, CharacterGlyphLayer, DeepComponent,
    AtomicElement, AtomicElementLayer, Proof, )

import os
import re
import zipfile


class Command(BaseCommand):

    help = 'Import .rcjk project'

    def __init__(self, *args, **kwargs):

        self._atomic_element_pattern = r'^(?P<project_name>[\w\-_]+)\.rcjk\/atomicElement\/(?P<glif_name>[\w\-\_]+)\.glif$'
        self._atomic_element_re = re.compile(self._atomic_element_pattern)

        self._atomic_element_layer_pattern = r'^(?P<project_name>[\w\-_]+)\.rcjk\/atomicElement\/(?P<layer_name>[\w\-\_]+)\/(?P<glif_name>[\w\-\_]+)\.glif$'
        self._atomic_element_layer_re = re.compile(self._atomic_element_layer_pattern)

        self._deep_component_pattern = r'^(?P<project_name>[\w\-_]+)\.rcjk\/deepComponent\/(?P<glif_name>[\w\-\_]+)\.glif$'
        self._deep_component_re = re.compile(self._deep_component_pattern)

        self._character_glyph_pattern = r'^(?P<project_name>[\w\-_]+)\.rcjk\/characterGlyph\/(?P<glif_name>[\w\-\_]+)\.glif$'
        self._character_glyph_re = re.compile(self._character_glyph_pattern)

        self._character_glyph_layer_pattern = r'^(?P<project_name>[\w\-_]+)\.rcjk\/characterGlyph\/(?P<layer_name>[\w\-\_]+)\/(?P<glif_name>[\w\-\_]+)\.glif$'
        self._character_glyph_layer_re = re.compile(self._character_glyph_layer_pattern)

    def handle(self, *args, **options):

#         AtomicElementLayer.objects.all().delete()
#         AtomicElement.objects.all().delete()
#         DeepComponent.objects.all().delete()
#         CharacterGlyphLayer.objects.all().delete()
#         CharacterGlyph.objects.all().delete()
#         return

        # TODO: project name and font name must be passed as arguments
        project_name = 'GS'
        font_name = 'Hanzi'

        # TODO: create font if not exist (get_or_create) ?!
        project_obj = Project.objects.get(name=project_name)
        font_obj = Font.objects.get(project=project_obj, name=font_name)

        filepath = '/root/robocjk/temp/Hanzi.rcjk.zip'

        # read and index zip files by type
        with zipfile.ZipFile(filepath, 'r') as file:

            # TODO: update fontlib and proofing from zip file

            names = file.namelist()
            names_dict = {
                'atomic_elements': [],
                'atomic_elements_layers': [],
                'deep_components': [],
                'character_glyphs': [],
                'character_glyphs_layers': [],
            }

            for name in names:

                match = self._character_glyph_re.match(name)
                if match:
                    names_dict['character_glyphs'].append((name, match, ))
                    continue

                match = self._character_glyph_layer_re.match(name)
                if match:
                    names_dict['character_glyphs_layers'].append((name, match, ))
                    continue

                match = self._deep_component_re.match(name)
                if match:
                    names_dict['deep_components'].append((name, match, ))
                    continue

                match = self._atomic_element_re.match(name)
                if match:
                    names_dict['atomic_elements'].append((name, match, ))
                    continue

                match = self._atomic_element_layer_re.match(name)
                if match:
                    names_dict['atomic_elements_layers'].append((name, match, ))
                    continue

            # import atomic elements
            for name, match in names_dict['atomic_elements']:
                self._import_atomic_element(
                    font_obj, self._zipfile_read(file, name), match)

            # import atomic elements layers
            for name, match in names_dict['atomic_elements_layers']:
                self._import_atomic_element_layer(
                    font_obj, self._zipfile_read(file, name), match)

            # import deep components
            for name, match in names_dict['deep_components']:
                self._import_deep_component(
                    font_obj, self._zipfile_read(file, name), match)

            # import character glyphs
            for name, match in names_dict['character_glyphs']:
                self._import_character_glyph(
                    font_obj, self._zipfile_read(file, name), match)

            # import character glyphs layers
            for name, match in names_dict['character_glyphs_layers']:
                self._import_character_glyph_layer(
                    font_obj, self._zipfile_read(file, name), match)

    def _zipfile_read(self, file, path, encoding='utf-8'):
        return str(file.read(path), encoding)

    def _import_glif(self, cls, font, content, match):
        data = GlifData()
        data.parse_string(content)
        obj, created = cls.objects.update_or_create(
            font=font, name=data.name, defaults={ 'data':content })
        print('Imported {}: {}'.format(
            cls, data.name))

    def _import_glif_layer(self, glif_cls, cls, font, content, match):
        data = GlifData()
        data.parse_string(content)
        layer_name = match.groupdict()['layer_name']
        glif_obj = glif_cls.objects.get(font=font, name=data.name)
        obj, created = cls.objects.update_or_create(
            glif=glif_obj, group_name=layer_name, defaults={ 'data':content })
        print('Imported {} [{}]: {}'.format(
            cls, layer_name, data.name))

    def _import_atomic_element(self, font, content, match):
        self._import_glif(AtomicElement, font, content, match)

    def _import_atomic_element_layer(self, font, content, match):
        self._import_glif_layer(AtomicElement, AtomicElementLayer, font, content, match)

    def _import_deep_component(self, font, content, match):
        self._import_glif(DeepComponent, font, content, match)

    def _import_character_glyph(self, font, content, match):
        self._import_glif(CharacterGlyph, font, content, match)

    def _import_character_glyph_layer(self, font, content, match):
        self._import_glif_layer(CharacterGlyph, CharacterGlyphLayer, font, content, match)

