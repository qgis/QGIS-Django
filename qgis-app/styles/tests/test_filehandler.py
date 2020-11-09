import os
from tempfile import NamedTemporaryFile

from django.core.exceptions import ValidationError
from django.test import TestCase

from styles.file_handler import read_xml_style, validator

STYLEFILE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'stylefiles'))


class XMLFileReadTest(TestCase):
    """
    Test the read_xml_style function.

    Read QGIS XML style files with 8 (eight) different types:
    - Fill Symbol.
    - Line Symbol.
    - Marker Symbol.
    - Color Ramp.
    - Text Format.
    - Label Setting.
    - Legend Patch.
    - 3D Symbol.
    """
    def setUp(self):
        """
        Setup before each test.
        """
        self.label_setting_file = os.path.join(STYLEFILE_DIR, "labelsettings.xml")
        self.legend_patch_file = os.path.join(STYLEFILE_DIR, "legend_patch.xml")
        self.color_ramp_file = os.path.join(STYLEFILE_DIR, "colorramp_blue.xml")
        self.symbol3d_file = os.path.join(STYLEFILE_DIR, "3d_cube.xml")
        self.text_format_file = os.path.join(STYLEFILE_DIR, "text-format.xml")
        self.symbol_line_file = os.path.join(STYLEFILE_DIR, "cattrail.xml")
        self.symbol_fill_file = os.path.join(STYLEFILE_DIR, "topo_swamp.xml")
        self.symbol_marker_file = os.path.join(STYLEFILE_DIR, "dotblack_marker.xml")

    def test_read_label_setting_file(self):
        read_file = read_xml_style(self.label_setting_file)
        style_type = read_file['type']
        style_name = read_file['name']
        self.assertEqual(style_type, "labelsetting")
        self.assertEqual(style_name, "Basic Label Setting")

    def test_read_legend_patch_file(self):
        read_file = read_xml_style(self.legend_patch_file)
        style_type = read_file['type']
        style_name = read_file['name']
        self.assertEqual(style_type, "legendpatchshape")
        self.assertEqual(style_name, "Building 3")

    def test_read_color_ramp_file(self):
        read_file = read_xml_style(self.color_ramp_file)
        style_type = read_file['type']
        style_name = read_file['name']
        self.assertEqual(style_type, "colorramp")
        self.assertEqual(style_name, "Blues")

    def test_read_symbol3d_file(self):
        read_file = read_xml_style(self.symbol3d_file)
        style_type = read_file['type']
        style_name = read_file['name']
        self.assertEqual(style_type, "symbol3d")
        self.assertEqual(style_name, "Cube")

    def test_read_text_format_file(self):
        read_file = read_xml_style(self.text_format_file)
        style_type = read_file['type']
        style_name = read_file['name']
        self.assertEqual(style_type, "textformat")
        self.assertEqual(style_name, "Basic Label")

    def test_read_symbol_line_file(self):
        read_file = read_xml_style(self.symbol_line_file)
        style_type = read_file['type']
        style_name = read_file['name']
        self.assertEqual(style_type, "line")
        self.assertEqual(style_name, "cat trail")

    def test_read_symbol_fill_file(self):
        read_file = read_xml_style(self.symbol_fill_file)
        style_type = read_file['type']
        style_name = read_file['name']
        self.assertEqual(style_type, "fill")
        self.assertEqual(style_name, "topo swamp")

    def test_read_symbol_marker_file(self):
        read_file = read_xml_style(self.symbol_marker_file)
        style_type = read_file['type']
        style_name = read_file['name']
        self.assertEqual(style_type, "marker")
        self.assertEqual(style_name, "dot  black")


class TestXMLValidator(TestCase):
    """
    Test the validator function.

    The validator should recognize the basic structure of a QGIS XML file.
    This test is using temporary file.
    """

    def test_valid_file(self):
        tf = NamedTemporaryFile(mode='w+t', suffix=".xml")
        tf.write("""<!DOCTYPE qgis_style>
<qgis_style version="2">
  <symbols/>
  <colorramps>
    <colorramp name="Blues" type="gradient">
      <prop k="color1" v="247,251,255,255"/>
      <prop k="color2" v="8,48,107,255"/>
      <prop k="discrete" v="0"/>
      <prop k="rampType" v="gradient"/>
      <prop k="stops" v="0.13;222,235,247,255:0.26;198,219,239,255:0.39;
      158,202,225,255:0.52;107,174,214,255:0.65;66,146,198,255:0.78;
      33,113,181,255:0.9;8,81,156,255"/>
    </colorramp>
  </colorramps>
  <textformats/>
  <labelsettings/>
  <legendpatchshapes/>
  <symbols3d/>
</qgis_style>
        """)
        tf.seek(0)
        validation = validator(tf)
        self.assertEqual(validation, True)
        assert validation == True
        tf.close()

    def test_invalid_xml(self):
        tf = NamedTemporaryFile(mode='w+t', suffix=".xml")
        tf.write("""<!DOCTYPE qgis_style>
        <qgis_style version="2">
          <symbols/>
          <colorramps>
            <colorramp name="Blues" type="gradient">
              <prop k="color1" v="247,251,255,255"/>
              <prop k="color2" v="8,48,107,255"/>
              <prop k="discrete" v="0"/>
              <prop k="rampType" v="gradient"/>
              <prop k="stops" v="0.13;222,235,247,255:0.26;198,219,239,
              255:0.39;158,202,225,255:0.52;107,174,214,255:0.65;66,146,
              198,255:0.78;33,113,181,255:0.9;8,81,156,255"/>
            </colorramp>
          </colorramps>
          <textformats/>
          <labelsettings/>
          <legendpatchshapes/>
          <symbols3d/>
                """)
        tf.seek(0)
        self.assertRaises(ValidationError, validator, tf)
        with self.assertRaisesMessage(ValidationError,
            "Cannot parse the style file. Please ensure your file is correct."):
            validator(tf)
        tf.close()

    def test_invalid_tag_root(self):
        tf = NamedTemporaryFile(mode='w+t', suffix=".xml")
        tf.write("""<!DOCTYPE qgis>
        <qgis version="2">
          <symbols/>
          <colorramps>
            <colorramp name="Blues" type="gradient">
              <prop k="color1" v="247,251,255,255"/>
              <prop k="color2" v="8,48,107,255"/>
              <prop k="discrete" v="0"/>
              <prop k="rampType" v="gradient"/>
              <prop k="stops" v="0.13;222,235,247,255:0.26;198,219,239,255:0.39;
              158,202,225,255:0.52;107,174,214,255:0.65;66,146,198,255:0.78;
              33,113,181,255:0.9;8,81,156,255"/>
            </colorramp>
          </colorramps>
          <textformats/>
          <labelsettings/>
          <legendpatchshapes/>
          <symbols3d/>
        </qgis>
                """)
        tf.seek(0)
        # self.assertRaises(ValidationError, validator, tf)
        with self.assertRaisesMessage(ValidationError,
            "Invalid root tag of style file. Please ensure your file is correct."):
            validator(tf)
        tf.close()

    def test_undefined_name_style(self):
        tf = NamedTemporaryFile(mode='w+t', suffix=".xml")
        tf.write("""<!DOCTYPE qgis_style>
        <qgis_style version="2">
          <symbols/>
          <colorramps>
            <colorramp type="gradient">
              <prop k="color1" v="247,251,255,255"/>
              <prop k="color2" v="8,48,107,255"/>
              <prop k="discrete" v="0"/>
              <prop k="rampType" v="gradient"/>
              <prop k="stops" v="0.13;222,235,247,255:0.26;198,219,239,255:0.39;
              158,202,225,255:0.52;107,174,214,255:0.65;66,146,198,255:0.78;
              33,113,181,255:0.9;8,81,156,255"/>
            </colorramp>
          </colorramps>
          <textformats/>
          <labelsettings/>
          <legendpatchshapes/>
          <symbols3d/>
        </qgis_style>
                """)
        tf.seek(0)
        with self.assertRaisesMessage(ValidationError,
            "Undefined style name. Please register your style type."):
            validator(tf)
        tf.close()

    def test_undefined_type_style(self):
        tf = NamedTemporaryFile(mode='w+t', suffix=".xml")
        tf.write("""<!DOCTYPE qgis_style>
<qgis_style version="2">
  <symbols>
    <symbol name="cat trail" clip_to_extent="1" tags="Showcase" force_rhr="0" alpha="1">
      
    </symbol>
  </symbols>
  <colorramps/>
  <textformats/>
  <labelsettings/>
  <legendpatchshapes/>
  <symbols3d/>
</qgis_style>
                """)
        tf.seek(0)
        with self.assertRaisesMessage(ValidationError,
            "Undefined style type. Please register your style type."):
            validator(tf)
        tf.close()
