# -*- coding: utf-8 -*-

from django.test import TestCase

from robocjk.core import GlifData

import fsutil


class CoreTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @staticmethod
    def _read_glif_data(filepath):
        glif_str = fsutil.read_file(fsutil.join_path(__file__, filepath))
        glif_data = GlifData()
        glif_data.parse_string(glif_str)
        return glif_data

    def test_glyph_data_with_invalid_xml_string(self):
        glif_data = GlifData()
        glif_data.parse_string('Hello World')
        self.assertFalse(glif_data.ok)
        self.assertTrue(isinstance(glif_data.error, Exception))
        self.assertEqual(glif_data.name, '')
        self.assertEqual(glif_data.filename, '')
        self.assertEqual(glif_data.unicode_hex, '')
        self.assertEqual(glif_data.components_names, [])
        self.assertEqual(glif_data.components_str, '')
        self.assertFalse(glif_data.has_components)
        self.assertFalse(glif_data.has_outlines)
        self.assertFalse(glif_data.has_unicode)
        self.assertFalse(glif_data.has_variation_axis)
        self.assertTrue(glif_data.is_empty)

    def test_glyph_data_with_atomic_element(self):
        glif_data = self._read_glif_data('test_core_data/atomicElement/line.glif')
        self.assertTrue(glif_data.ok)
        self.assertEqual(glif_data.error, None)
        self.assertEqual(glif_data.name, 'line')
        self.assertEqual(glif_data.filename, 'line.glif')
        self.assertEqual(glif_data.unicode_hex, '')
        self.assertEqual(glif_data.components_names, [])
        self.assertEqual(glif_data.components_str, '')
        self.assertFalse(glif_data.has_components)
        self.assertTrue(glif_data.has_outlines)
        self.assertFalse(glif_data.has_unicode)
        self.assertTrue(glif_data.has_variation_axis)
        self.assertFalse(glif_data.is_empty)

    def test_glyph_data_with_deep_component(self):
        glif_data = self._read_glif_data('test_core_data/deepComponent/D_C__98E_0_00.glif')
        self.assertTrue(glif_data.ok)
        self.assertEqual(glif_data.error, None)
        self.assertEqual(glif_data.name, 'DC_98E0_00')
        self.assertEqual(glif_data.filename, 'D_C__98E_0_00.glif')
        self.assertEqual(glif_data.unicode_hex, '')
        self.assertEqual(glif_data.components_names, ['bendingBoth', 'bendingBothOp', 'line', 'ShuTi', 'taperingLineRight'])
        self.assertEqual(glif_data.components_str, 'bendingBoth,bendingBothOp,line,ShuTi,taperingLineRight')
        self.assertTrue(glif_data.has_components)
        self.assertFalse(glif_data.has_outlines)
        self.assertFalse(glif_data.has_unicode)
        self.assertTrue(glif_data.has_variation_axis)
        self.assertFalse(glif_data.is_empty)

    def test_glyph_data_with_deep_component_empty(self):
        glif_data = self._read_glif_data('test_core_data/deepComponent/D_C__9E_1F__00.glif')
        self.assertTrue(glif_data.ok)
        self.assertEqual(glif_data.error, None)
        self.assertEqual(glif_data.name, 'DC_9E1F_00')
        self.assertEqual(glif_data.filename, 'D_C__9E_1F__00.glif')
        self.assertEqual(glif_data.unicode_hex, '')
        self.assertEqual(glif_data.components_names, [])
        self.assertEqual(glif_data.components_str, '')
        self.assertFalse(glif_data.has_components)
        self.assertFalse(glif_data.has_outlines)
        self.assertFalse(glif_data.has_unicode)
        self.assertFalse(glif_data.has_variation_axis)
        self.assertTrue(glif_data.is_empty)

    def test_glyph_data_with_character_glyph(self):
        glif_data = self._read_glif_data('test_core_data/characterGlyph/uni346C_.glif')
        self.assertTrue(glif_data.ok)
        self.assertEqual(glif_data.error, None)
        self.assertEqual(glif_data.name, 'uni346C')
        self.assertEqual(glif_data.filename, 'uni346C_.glif')
        self.assertEqual(glif_data.unicode_hex, '346C')
        self.assertEqual(glif_data.components_names, ['DC_4EBB_00', 'DC_5341_00', 'DC_53E3_00', 'DC_5973_01'])
        self.assertEqual(glif_data.components_str, 'DC_4EBB_00,DC_5341_00,DC_53E3_00,DC_5973_01')
        self.assertTrue(glif_data.has_components)
        self.assertFalse(glif_data.has_outlines)
        self.assertTrue(glif_data.has_unicode)
        self.assertFalse(glif_data.has_variation_axis)
        self.assertFalse(glif_data.is_empty)


    def test_glyph_data_with_character_glyph_empty(self):
        glif_data = self._read_glif_data('test_core_data/characterGlyph/uni3413.glif')
        self.assertTrue(glif_data.ok)
        self.assertEqual(glif_data.error, None)
        self.assertEqual(glif_data.name, 'uni3413')
        self.assertEqual(glif_data.filename, 'uni3413.glif')
        self.assertEqual(glif_data.unicode_hex, '3413')
        self.assertEqual(glif_data.components_names, [])
        self.assertEqual(glif_data.components_str, '')
        self.assertFalse(glif_data.has_components)
        self.assertFalse(glif_data.has_outlines)
        self.assertTrue(glif_data.has_unicode)
        self.assertFalse(glif_data.has_variation_axis)
        self.assertTrue(glif_data.is_empty)

    def test_glyph_data_marker_color(self):
        glif_data = self._read_glif_data('test_core_data/characterGlyph/cieuc.glif')
        # print(glif_data.status_color)
        self.assertEqual(glif_data.status_color, '1,0,0,1')
