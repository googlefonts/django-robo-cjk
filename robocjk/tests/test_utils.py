from django.test import TestCase

from robocjk.utils import (
    char_to_unicode,
    format_glif,
    unicode_to_char,
    unicodes_str_to_list,
    username_to_filename,
)


class UtilsTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None
        pass

    def tearDown(self):
        pass

    def test_char_to_unicode(self):
        self.assertEqual(char_to_unicode("丒"), "4E12")

    def test_unicode_to_char(self):
        self.assertEqual(unicode_to_char("4E12"), "丒")

    def test_unicodes_str_to_list(self):
        f = unicodes_str_to_list
        self.assertEqual(f(None), [])
        self.assertEqual(f(""), [])
        self.assertEqual(f("4E12"), ["4E12"])
        self.assertEqual(f("4E12,4E13"), ["4E12", "4E13"])
        self.assertEqual(f("4E12,4E13,4E14"), ["4E12", "4E13", "4E14"])

    def test_unicodes_str_to_int_list(self):
        f = unicodes_str_to_list
        self.assertEqual(f(None, to_int=True), [])
        self.assertEqual(f("", to_int=True), [])
        self.assertEqual(f("4E12", to_int=True), [19986])
        self.assertEqual(f("4E12,4E13", to_int=True), [19986, 19987])
        self.assertEqual(f("4E12,4E13,4E14", to_int=True), [19986, 19987, 19988])

    def test_username_to_filename(self):
        f = username_to_filename
        self.assertEqual(f("a"), "a")
        self.assertEqual(f("A"), "A_")
        self.assertEqual(f("AE"), "A_E_")
        self.assertEqual(f("Ae"), "A_e")
        self.assertEqual(f("ae"), "ae")
        self.assertEqual(f("aE"), "aE_")
        self.assertEqual(f("a.alt"), "a.alt")
        self.assertEqual(f("A.alt"), "A_.alt")
        self.assertEqual(f("A.Alt"), "A_.A_lt")
        self.assertEqual(f("A.aLt"), "A_.aL_t")
        self.assertEqual(f("A.alT"), "A_.alT_")
        self.assertEqual(f("T_H"), "T__H_")
        self.assertEqual(f("T_h"), "T__h")
        self.assertEqual(f("t_h"), "t_h")
        self.assertEqual(f("F_F_I"), "F__F__I_")
        self.assertEqual(f("f_f_i"), "f_f_i")
        self.assertEqual(f("Aacute_V.swash"), "A_acute_V_.swash")
        self.assertEqual(f(".notdef"), "_notdef")
        self.assertEqual(f("con"), "_con")
        self.assertEqual(f("CON"), "C_O_N_")
        self.assertEqual(f("con.alt"), "_con.alt")
        self.assertEqual(f("alt.con"), "alt._con")

    def test_format_glif(self):
        s = """<?xml version='1.0' encoding='UTF-8'?>
<glyph name="uni000A" format="2"> <advance width="1000" /> <unicode hex="000A" />
<outline> </outline> <lib> <dict> <key>public.markColor</key> <string>1,0,0,1</string>
<key>robocjk.axes</key> <array> <dict> <key>maxValue</key> <real>1.0</real>
<key>minValue</key> <real>0.0</real> <key>name</key> <string>wght</string> </dict> </array> <key>robocjk.deepComponents</key> <array />
<key>robocjk.variationGlyphs</key> <array> <dict> <key>deepComponents</key> <array /> <key>layerName</key>
<string>wght</string> <key>location</key> <dict> <key>wght</key> <real>1.0</real> </dict> <key>on</key>
<integer>1</integer> <key>sourceName</key> <string>wght</string> </dict> </array> </dict> </lib> </glyph>"""
        result = format_glif(s)
        expected_result = """<?xml version='1.0' encoding='UTF-8'?>
<glyph name="uni000A" format="2">
  <advance width="1000"/>
  <unicode hex="000A"/>
  <outline>
  </outline>
  <lib>
    <dict>
      <key>public.markColor</key>
      <string>1,0,0,1</string>
      <key>robocjk.axes</key>
      <array>
        <dict>
          <key>maxValue</key>
          <real>1.0</real>
          <key>minValue</key>
          <real>0.0</real>
          <key>name</key>
          <string>wght</string>
        </dict>
      </array>
      <key>robocjk.deepComponents</key>
      <array/>
      <key>robocjk.variationGlyphs</key>
      <array>
        <dict>
          <key>deepComponents</key>
          <array/>
          <key>layerName</key>
          <string>wght</string>
          <key>location</key>
          <dict>
            <key>wght</key>
            <real>1.0</real>
          </dict>
          <key>on</key>
          <integer>1</integer>
          <key>sourceName</key>
          <string>wght</string>
        </dict>
      </array>
    </dict>
  </lib>
</glyph>
"""
        self.assertEqual(result, expected_result)
