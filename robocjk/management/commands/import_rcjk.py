# -*- coding: utf-8 -*-

from benedict import benedict

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from robocjk.core import GlifData
from robocjk.models import (
    Project, Font, CharacterGlyph, CharacterGlyphLayer, DeepComponent,
    AtomicElement, AtomicElementLayer, Proof, )

import fsutil
import os
import re
import zipfile


class Command(BaseCommand):

    help = 'Import .rcjk project'

    def __init__(self, *args, **kwargs):

        super(Command, self).__init__(*args, **kwargs)

        self._font_pattern = r'((?P<font_name>[\w\-_]+)\.rcjk\/)'

        self._fontlib_pattern = r'^{}?fontLib\.json$'.format(self._font_pattern)
        self._fontlib_re = re.compile(self._fontlib_pattern)

        self._atomic_element_pattern = r'^{}?atomicElement\/(?P<glif_name>[\w\-\_]+)\.glif$'.format(self._font_pattern)
        self._atomic_element_re = re.compile(self._atomic_element_pattern)

        self._atomic_element_layer_pattern = r'^{}?atomicElement\/(?P<layer_name>[\w\-\_]+)\/(?P<glif_name>[\w\-\_]+)\.glif$'.format(self._font_pattern)
        self._atomic_element_layer_re = re.compile(self._atomic_element_layer_pattern)

        self._deep_component_pattern = r'^{}?deepComponent\/(?P<glif_name>[\w\-\_]+)\.glif$'.format(self._font_pattern)
        self._deep_component_re = re.compile(self._deep_component_pattern)

        self._character_glyph_pattern = r'^{}?characterGlyph\/(?P<glif_name>[\w\-\_]+)\.glif$'.format(self._font_pattern)
        self._character_glyph_re = re.compile(self._character_glyph_pattern)

        self._character_glyph_layer_pattern = r'^{}?characterGlyph\/(?P<layer_name>[\w\-\_]+)\/(?P<glif_name>[\w\-\_]+)\.glif$'.format(self._font_pattern)
        self._character_glyph_layer_re = re.compile(self._character_glyph_layer_pattern)

    def add_arguments(self, parser):
        # https://docs.python.org/3/library/argparse.html
        parser.add_argument(
            '--filepath',
            required=True,
            help='The zipped .rcjk filepath. The filepath must be absolute or relative to "/root/robocjk/temp/"',
        )
        parser.add_argument(
            '--font-uid',
            required=True,
            help='The uid "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" of the font into which the .rcjk files will be imported.',
        )
        parser.add_argument(
            '--font-clear',
            action='store_true',
            help='Delete existing Atomic Elements, Atomic Elements Layers, Deep Components, '
                 'Character Glyphs, Character Glyphs Layers before importing new .rcjk file.',
        )

    def handle(self, *args, **options):

        filepath = options.get('filepath')
        if not filepath.startswith('/'):
            filepath = os.path.join('/root/robocjk/temp/', filepath)
        if not filepath.endswith('.rcjk.zip'):
            raise CommandError('Invalid filepath, expected an "*.rcjk.zip" file.')
        if not fsutil.exists(filepath):
            raise CommandError('Invalid filepath, file "{}" doesn\'t exist.'.format(filepath))

        font_uid = options.get('font_uid')
        try:
            font_obj = Font.objects.select_related('project').get(uid=font_uid)
        except Font.DoesNotExist:
            raise CommandError('Invalid font_uid, font with uid "{}" doesn\'t exist.'.format(font_uid))

        font_obj.available = False
        font_obj.save()

        font_clear = options.get('font_clear', False)
        if font_clear:
            print('Deleting existing atomic elements...')
            AtomicElement.objects.filter(font__uid=font_uid).delete()
            print('Deleting existing deep components...')
            DeepComponent.objects.filter(font__uid=font_uid).delete()
            print('Deleting existing character glyphs...')
            CharacterGlyph.objects.filter(font__uid=font_uid).delete()

        # read and index zip files by type
        with zipfile.ZipFile(filepath, 'r') as file:

            names = file.namelist()
            names_dict = {
                'atomic_elements': [],
                'atomic_elements_layers': [],
                'deep_components': [],
                'character_glyphs': [],
                'character_glyphs_layers': [],
                'fontlib': [],
            }

            for name in names:
                # print(name)

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

                match = self._fontlib_re.match(name)
                if match:
                    names_dict['fontlib'].append((name, match, ))
                    continue

            print('Found {} atomic elements to import.'.format(
                len(names_dict['atomic_elements'])))

            print('Found {} atomic elements layers to import.'.format(
                len(names_dict['atomic_elements_layers'])))

            print('Found {} deep components to import.'.format(
                len(names_dict['deep_components'])))

            print('Found {} character glyphs to import.'.format(
                len(names_dict['character_glyphs'])))

            print('Found {} character glyphs layers to import.'.format(
                len(names_dict['character_glyphs_layers'])))

            print('Found {} fontlib to import.'.format(
                len(names_dict['fontlib'])))

            # import fontlib
            for name, match in names_dict['fontlib']:
                self._import_fontlib(
                    font_obj, self._zipfile_read(file, name), match)

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

            # import character glyphs layers
            for name, match in names_dict['character_glyphs_layers']:
                self._import_character_glyph_layer(
                    font_obj, self._zipfile_read(file, name), match)

        # font_obj.project.save_to_file_system()
        font_obj.available = True
        font_obj.save()

    def _zipfile_read(self, file, path, encoding='utf-8'):
        return str(file.read(path), encoding)

    def _import_fontlib(self, font, content, match):
        font.fontlib = benedict.from_json(content, keypath_separator=None)
        font.save()

    def _import_glif(self, cls, font, content, match):
        data = GlifData()
        data.parse_string(content)
        obj, created = cls.objects.update_or_create(
            font=font, name=data.name, defaults={ 'data':content })
        print('Imported {}: {}'.format(cls, data.name))

    def _import_glif_layer(self, glif_cls, cls, font, content, match):
        data = GlifData()
        data.parse_string(content)
        layer_name = match.groupdict()['layer_name']
        try:
            glif_obj = glif_cls.objects.get(font=font, name=data.name)
        except glif_cls.DoesNotExist:
            print('Import Error {} [{}]: {}'.format(cls, layer_name, data.name))
            return
        obj, created = cls.objects.update_or_create(
            glif=glif_obj, group_name=layer_name, defaults={ 'data':content })
        print('Imported {} [{}]: {}'.format(cls, layer_name, data.name))

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
