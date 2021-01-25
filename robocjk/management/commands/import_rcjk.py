# -*- coding: utf-8 -*-

from benedict import benedict

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from robocjk.core import GlifData
from robocjk.models import (
    Project, Font, CharacterGlyph, CharacterGlyphLayer, DeepComponent,
    AtomicElement, AtomicElementLayer, Proof, StatusModel, )

import fsutil
import re
import zipfile


class Command(BaseCommand):

    help = 'Import .rcjk project'

    def __init__(self, *args, **kwargs):

        super(Command, self).__init__(*args, **kwargs)

        self._font_pattern = r'((?P<font_name>[\w\-_\.]+)\.rcjk\/)'
        self._fontlib_pattern = r'^{}?fontLib\.json$'.format(self._font_pattern)
        self._features_pattern = r'^{}?features\.fea$'.format(self._font_pattern)
        self._atomic_element_pattern = r'^{}?atomicElement\/(?P<glif_name>[\w\-\_\.\+]+)\.glif$'.format(self._font_pattern)
        self._atomic_element_layer_pattern = r'^{}?atomicElement\/(?P<layer_name>[\w\-\_\.\+]+)\/(?P<glif_name>[\w\-\_\.\+]+)\.glif$'.format(self._font_pattern)
        self._deep_component_pattern = r'^{}?deepComponent\/(?P<glif_name>[\w\-\_\.\+]+)\.glif$'.format(self._font_pattern)
        self._character_glyph_pattern = r'^{}?characterGlyph\/(?P<glif_name>[\w\-\_\.\+]+)\.glif$'.format(self._font_pattern)
        self._character_glyph_layer_pattern = r'^{}?characterGlyph\/(?P<layer_name>[\w\-\_\.\+]+)\/(?P<glif_name>[\w\-\_\.\+]+)\.glif$'.format(self._font_pattern)

        self._import_mappings = [
            {
                'pattern': self._character_glyph_pattern,
                'group_name': 'character_glyphs',
                'import_func': self._import_character_glyph,
            },
            {
                'pattern': self._character_glyph_layer_pattern,
                'group_name': 'character_glyphs_layers',
                'import_func': self._import_character_glyph_layer,
            },
            {
                'pattern': self._deep_component_pattern,
                'group_name': 'deep_components',
                'import_func': self._import_deep_component,
            },
            {
                'pattern': self._atomic_element_pattern,
                'group_name': 'atomic_elements',
                'import_func': self._import_atomic_element,
            },
            {
                'pattern': self._atomic_element_layer_pattern,
                'group_name': 'atomic_elements_layers',
                'import_func': self._import_atomic_element_layer,
            },
            {
                'pattern': self._fontlib_pattern,
                'group_name': 'fontlib',
                'import_func': self._import_fontlib,
            },
            {
                'pattern': self._features_pattern,
                'group_name': 'features',
                'import_func': self._import_features,
            },
        ]

        for item in self._import_mappings:
            item['pattern_re'] = re.compile(item['pattern'])

        self._import_groups = {
            item['group_name']:[] for item in self._import_mappings
        }


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
            filepath = fsutil.join_path('/root/robocjk/temp/', filepath)
        if not filepath.endswith('.zip'):
            message = 'Invalid filepath, expected a .zip file containing .rcjk font project.'
            self.stderr.write(message)
            raise CommandError(message)
        if not fsutil.exists(filepath):
            message = 'Invalid filepath, file "{}" doesn\'t exist.'.format(filepath)
            self.stderr.write(message)
            raise CommandError(message)

        font_uid = options.get('font_uid')
        try:
            font_obj = Font.objects.select_related('project').get(uid=font_uid)
        except Font.DoesNotExist:
            message = 'Invalid font_uid, font with uid "{}" doesn\'t exist.'.format(font_uid)
            self.stderr.write(message)
            raise CommandError(message)

        font_obj.available = False
        font_obj.save()

        font_clear = options.get('font_clear', False)
        if font_clear:
            self.stdout.write('Deleting existing atomic elements...')
            AtomicElement.objects.filter(font__uid=font_uid).delete()
            self.stdout.write('Deleting existing deep components...')
            DeepComponent.objects.filter(font__uid=font_uid).delete()
            self.stdout.write('Deleting existing character glyphs...')
            CharacterGlyph.objects.filter(font__uid=font_uid).delete()

        # read and index zip files by type
        with zipfile.ZipFile(filepath, 'r') as file:
            names = file.namelist()

            for name in names:
                for item in self._import_mappings:
                    match = item['pattern_re'].match(name)
                    if match:
                        self._import_groups[item['group_name']].append((name, match, ))
                        continue

            for item in self._import_mappings:
                group_name = item['group_name']
                self.stdout.write('Found {} {} to import.'.format(
                    len(self._import_groups[group_name]), group_name.replace('_', ' ').title()))

            for item in self._import_mappings:
                for name, match in self._import_groups[item['group_name']]:
                    item['import_func'](font_obj, self._zipfile_read(file, name), match)

        font_obj.available = True
        font_obj.save()

    def _zipfile_read(self, file, path, encoding='utf-8'):
        return str(file.read(path), encoding)

    def _import_fontlib(self, font, content, match):
        font.fontlib = benedict.from_json(content, keypath_separator=None)
        font.save()

    def _import_features(self, font, content, match):
        font.features = content
        font.save()

    def _import_glif(self, cls, font, content, match):
        data = GlifData()
        data.parse_string(content)
        # parse status from mark color during import
        status_color = data.status_color
        status = None
        if status_color:
            status = StatusModel.STATUS_MARK_COLORS.get(status_color, None)
        if status is None:
            status = StatusModel.STATUS_WIP
        obj, created = cls.objects.update_or_create(
            font=font, name=data.name, defaults={ 'status':status, 'data':content })
        # self.stdout.write('Imported {}: {}'.format(cls, data.name))

    def _import_glif_layer(self, glif_cls, cls, font, content, match):
        data = GlifData()
        data.parse_string(content)
        layer_name = match.groupdict()['layer_name']
        try:
            glif_obj = glif_cls.objects.get(font=font, name=data.name)
        except glif_cls.DoesNotExist:
            self.stderr.write('Import Error {} [{}]: {}'.format(cls, layer_name, data.name))
            return
        obj, created = cls.objects.update_or_create(
            glif=glif_obj, group_name=layer_name, defaults={ 'data':content })
        # self.stdout.write('Imported {} [{}]: {}'.format(cls, layer_name, data.name))

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
