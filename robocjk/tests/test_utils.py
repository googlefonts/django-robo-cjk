# -*- coding: utf-8 -*-

from django.test import TestCase

from robocjk.utils import char_to_unicode, unicode_to_char, username_to_filename


class UtilsTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_char_to_unicode(self):
        self.assertEqual(char_to_unicode('丒'), '4E12')

    def test_unicode_to_char(self):
        self.assertEqual(unicode_to_char('4E12'), '丒')

    def test_username_to_filename(self):
        f = username_to_filename
        self.assertEqual(f('a'), 'a')
        self.assertEqual(f('A'), 'A_')
        self.assertEqual(f('AE'), 'A_E_')
        self.assertEqual(f('Ae'), 'A_e')
        self.assertEqual(f('ae'), 'ae')
        self.assertEqual(f('aE'), 'aE_')
        self.assertEqual(f('a.alt'), 'a.alt')
        self.assertEqual(f('A.alt'), 'A_.alt')
        self.assertEqual(f('A.Alt'), 'A_.A_lt')
        self.assertEqual(f('A.aLt'), 'A_.aL_t')
        self.assertEqual(f('A.alT'), 'A_.alT_')
        self.assertEqual(f('T_H'), 'T__H_')
        self.assertEqual(f('T_h'), 'T__h')
        self.assertEqual(f('t_h'), 't_h')
        self.assertEqual(f('F_F_I'), 'F__F__I_')
        self.assertEqual(f('f_f_i'), 'f_f_i')
        self.assertEqual(f('Aacute_V.swash'), 'A_acute_V_.swash')
        self.assertEqual(f('.notdef'), '_notdef')
        self.assertEqual(f('con'), '_con')
        self.assertEqual(f('CON'), 'C_O_N_')
        self.assertEqual(f('con.alt'), '_con.alt')
        self.assertEqual(f('alt.con'), 'alt._con')
