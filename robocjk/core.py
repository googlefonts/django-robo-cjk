# -*- coding: utf-8 -*-

# from django.conf import settings

from benedict import benedict
from xml.etree import ElementTree

from robocjk.debug import logger
from robocjk.utils import username_to_filename


class GlifData(object):

    _error = None
    _xml_string = None
    _xml = None
    _lib = None
    _name = ''
    _filename = ''
    _unicode_hex = ''
    _components_names = None
    _components_str = ''
    _has_components = False
    _has_outlines = False
    _has_unicode = False
    _has_variation_axis = False
    _is_empty = True
    _ok = False

    def __init__(self, *args):
        super(GlifData, self).__init__()

    def parse_file(self, fp):
        self._ok = False
        try:
            self._xml = ElementTree.parse(fp)
        except ElementTree.ParseError as xml_data_error:
            self._error = xml_data_error
            return
        try:
            self._parse_data()
        except Exception as xml_parse_error:
            self._error = xml_parse_error
            return
        self._ok = True

    def parse_string(self, s):
        self._ok = False
        self._error = None
        try:
            self._xml_string = s
            self._xml = ElementTree.fromstring(self._xml_string)
        except ElementTree.ParseError as xml_data_error:
            self._error = xml_data_error
            return
        try:
            self._parse_data()
        except Exception as xml_parse_error:
            self._error = xml_parse_error
            return
        self._ok = True

    def _parse_data(self):
        # parse name and generate filename
        self._name = self._xml.get('name')
        if not self._name:
            raise ValueError('Invalid name, name cannot be "".'.format(self._name))

        self._filename = '{}.glif'.format(username_to_filename(self.name))

        # look for glyph unicode hex value
        unicode_xml = self._xml.find('./unicode')
        if unicode_xml is not None:
            self._unicode_hex = unicode_xml.get('hex')
            self._has_unicode = bool(self._unicode_hex != '')

        # look for <lib><dict> xml node
        lib_xml = self._xml.find('./lib/dict')
        if lib_xml is not None:
            lib_str = ElementTree.tostring(lib_xml).decode()

            # parse lib as plist
            self._lib = benedict.from_plist(lib_str, keypath_separator='/')

            # parse components list
            components_list = self._lib.get('robocjk.deepComponents', [])
            self._components_names = { item.get('name') for item in components_list}
            if '' in self._components_names:
                self._components_names.remove('')
            self._components_str = ','.join({'{}'.format(item) for item in self._components_names})

            # update computed properties
            self._has_components = bool(components_list)
            self._has_variation_axis = bool(self._lib.get('robocjk.glyphVariationGlyphs'))

        # update computed properties
        self._has_outlines = bool(self._xml.find('./outline'))
        self._is_empty = (not self._has_outlines and not self._has_components)

    @property
    def error(self):
        return self._error

    @property
    def xml_string(self):
        return self._xml_string

    @property
    def xml(self):
        return self._xml

    @property
    def lib(self):
        return self._lib

    @property
    def name(self):
        return self._name

    @property
    def filename(self):
        return self._filename

    @property
    def unicode_hex(self):
        return self._unicode_hex

    @property
    def components_names(self):
        return self._components_names

    @property
    def components_str(self):
        return self._components_str

    @property
    def has_components(self):
        return self._has_components

    @property
    def has_outlines(self):
        return self._has_outlines

    @property
    def has_unicode(self):
        return self._has_unicode

    @property
    def has_variation_axis(self):
        return self._has_variation_axis

    @property
    def is_empty(self):
        return self._is_empty

    @property
    def ok(self):
        return self._ok


# class GlyphsCompositionData(object):
#
#     @staticmethod
#     def read():
#         """
#         Read data from https://github.com/BlackFoundryCom/HanGlyphComposition/blob/master/GlyphsDeepComposition/Characters2DeepComponents.txt
#         and return a generator of [character-glyph, deep-components]
#         """
#         filepath = os.path.join(
#             settings.BASE_DIR,
#             'robocjk/data/characters-glyphs-to-deep-components.txt')
#         # print(filepath)
#         with open(filepath, 'r') as file:
#             lines = file.readlines()
#             for line in lines:
#                 # print(line)
#                 yield line.split(':')
#
#
#     _character_glyphs = None
#     _deep_components = None
#     _deep_components_by_character_glyph = None
#
#     def __init__(self, *args, **kwargs):
#         # list of unique character glyphs values
#         self._character_glyphs = []
#         # list of unique deep components values
#         self._deep_components = []
#         # deep components indexed by character glyph
#         self._deep_components_by_character_glyph = {}
#
#         for character_glyph, deep_components in self.read():
#             self._character_glyphs.append(character_glyph)
#
#             # build list of unique deep components
#             deep_components_list = list(deep_components)
#             for deep_component in deep_components_list:
#                 if deep_component not in self._deep_components:
#                     self._deep_components.append(deep_component)
#
#             # index deep components by character glyph for quick lookup
#             self._deep_components_by_character_glyph[character_glyph] = deep_components_list
#
#     def get_character_glyphs(self):
#         """
#         Return the list of unique character-glyphs values.
#         """
#         return self._character_glyphs
#
#     def get_deep_components(self):
#         """
#         Return the list of unique deep-components values.
#         """
#         return self._deep_components
#
#     def get_deep_components_by_character_glyph(self, character_glyph):
#         """
#         Return deep components list for the given character-glyph.
#         """
#         return self._deep_components_by_character_glyph.get(character_glyph, None)

