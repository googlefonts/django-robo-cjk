# -*- coding: utf-8 -*-

from django.test import TestCase

from robocjk.models import (
    Project, Font, CharacterGlyph, CharacterGlyphLayer, DeepComponent,
    AtomicElement, AtomicElementLayer, Proof, StatusModel, )

import fsutil


class ModelsTestCase(TestCase):

    @classmethod
    def read_glif_data(cls, path):
        glifpath = fsutil.join_path(__file__, 'test_models_data', path)
        glifdata = fsutil.read_file(glifpath)
        return glifdata

    def setUp(self):
        self._project = Project.objects.create(name='My Font Family')

        self._font1 = Font.objects.create(project=self._project, name='My Font 1')
        self._font2 = Font.objects.create(project=self._project, name='My Font 2')

        self._atomic_element = AtomicElement.objects.create(
            font=self._font1,
            data=self.read_glif_data('atomicElement/bendingB_oth.glif'))

        self._atomic_element_layer = AtomicElementLayer.objects.create(
            group_name='1',
            glif=self._atomic_element,
            data=self.read_glif_data('atomicElement/1/bendingB_oth.glif'))

        self._deep_component = DeepComponent.objects.create(
            font=self._font1,
            data=self.read_glif_data('deepComponent/D_C__2B_740_00.glif'))

        self._character_glyph = CharacterGlyph.objects.create(
            font=self._font1,
            data=self.read_glif_data('characterGlyph/uni4E_25.glif'))

        self._character_glyph_layer = CharacterGlyphLayer.objects.create(
            group_name='1',
            glif=self._character_glyph,
            data=self.read_glif_data('characterGlyph/1/uni4E_25.glif'))

        self._character_glyph.deep_components.add(self._deep_component)

    def tearDown(self):
        pass

    def test_project(self):
        self.assertEqual(self._project.name, 'My Font Family')
        self.assertEqual(self._project.slug, 'my-font-family')
        self.assertTrue(len(str(self._project.uid)) == 36)
        self.assertTrue(len(self._project.hashid) >= 7)
        self.assertEqual(list(self._project.fonts.all()), [self._font1, self._font2])
        self.assertEqual(self._project.num_fonts(), 2)
        self.assertTrue(isinstance(self._project.serialize(), dict))
        # print(self._project.path())
        # self.assertTrue(self._project.path())

    def test_font(self):
        self.assertEqual(self._font1.project, self._project)
        self.assertEqual(self._font1.slug, 'my-font-1')
        self.assertTrue(len(str(self._font1.uid)) == 36)
        self.assertTrue(len(self._font1.hashid) >= 7)
        self.assertEqual(self._font1.num_character_glyphs(), 1)
        self.assertEqual(self._font1.num_deep_components(), 1)
        self.assertEqual(self._font1.num_atomic_elements(), 1)
        self.assertTrue(isinstance(self._font1.serialize(), dict))

    def test_character_glyph(self):
        self.assertEqual(self._character_glyph.font, self._font1)
        self.assertEqual(self._character_glyph.name, 'uni4E25')
        self.assertEqual(self._character_glyph.unicode_hex, '4E25')
        self.assertEqual(self._character_glyph.filename, 'uni4E_25.glif')
        self.assertEqual(list(self._character_glyph.layers.all()), [self._character_glyph_layer])
        self.assertEqual(list(self._character_glyph.deep_components.all()), [self._deep_component])
        self.assertTrue(isinstance(self._character_glyph.serialize(), dict))
        self.assertEqual(self._character_glyph.status, StatusModel.STATUS_TODO)

    def test_character_glyph_layer(self):
        self.assertEqual(self._character_glyph_layer.glif, self._character_glyph)
        self.assertEqual(self._character_glyph_layer.group_name, '1')
        self.assertEqual(self._character_glyph_layer.name, 'uni4E25')
        self.assertEqual(self._character_glyph_layer.unicode_hex, '4E25')
        self.assertEqual(self._character_glyph_layer.filename, 'uni4E_25.glif')
        self.assertTrue(isinstance(self._character_glyph_layer.serialize(), dict))

    def test_deep_component(self):
        self.assertEqual(self._deep_component.font, self._font1)
        self.assertEqual(self._deep_component.name, 'DC_2B740_00')
        self.assertEqual(self._deep_component.unicode_hex, '')
        self.assertEqual(self._deep_component.filename, 'D_C__2B_740_00.glif')
        self.assertTrue(isinstance(self._deep_component.serialize(), dict))
        self.assertEqual(self._deep_component.status, StatusModel.STATUS_TODO)

    def test_atomic_element(self):
        self.assertEqual(self._atomic_element.font, self._font1)
        self.assertEqual(self._atomic_element.name, 'bendingBoth')
        self.assertEqual(self._atomic_element.unicode_hex, '')
        self.assertEqual(self._atomic_element.filename, 'bendingB_oth.glif')
        self.assertEqual(list(self._atomic_element.layers.all()), [self._atomic_element_layer])
        self.assertTrue(isinstance(self._atomic_element.serialize(), dict))
        self.assertEqual(self._atomic_element.status, StatusModel.STATUS_TODO)

    def test_atomic_element_layer(self):
        self.assertEqual(self._atomic_element_layer.glif, self._atomic_element)
        self.assertEqual(self._atomic_element_layer.group_name, '1')
        self.assertEqual(self._atomic_element_layer.name, 'bendingBoth')
        self.assertEqual(self._atomic_element_layer.unicode_hex, '')
        self.assertEqual(self._atomic_element_layer.filename, 'bendingB_oth.glif')
        self.assertTrue(isinstance(self._atomic_element_layer.serialize(), dict))
