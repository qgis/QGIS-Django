"""
Validator for Style XML file.
"""
import xml.etree.ElementTree as ET

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def _check_name_type_attribute(element):
    """
    Check if element has name and type attribute.
    """
    style_name = element.get('name')
    if not style_name:
        raise ValidationError(_('Undefined style name. '
                                'Please register your style type.'))
    if element.tag == 'symbol':
        style_type = element.get('type')
        if not style_type:
            raise ValidationError(_('Undefined style type. '
                                    'Please register your style type.'))


def validator(xmlfile):
    """
    Validate a style file for a Form.

    The file should be a valid XML file.
    The file should contains:
    - qgis_style tag in root.
    - attribute name and type in symbol tag.

    This validation will pass a style file with style types:
    - Symbol : Fill
    - Symbol : Line
    - Symbol : Marker
    - Color Ramp
    - Label Setting
    - Legend Patch
    - Text Format
    - 3D Symbol
    """

    try:
        tree = ET.parse(xmlfile)
    except ET.ParseError:
        raise ValidationError(_('Cannot parse the style file. '
                                'Please ensure your file is correct.'))
    root = tree.getroot()
    if not root or not root.tag == 'qgis_style':
        raise ValidationError(_('Invalid root tag of style file. '
                                'Please ensure your file is correct.'))
    # find child elements
    symbol = root.find('./symbols/symbol')
    colorramp = root.find('./colorramps/colorramp')
    labelsetting = root.find('./labelsettings/labelsetting')
    legendpatchshape = root.find('./legendpatchshapes/legendpatchshape')
    symbol3d = root.find('./symbols3d/symbol3d')
    textformat = root.find('./textformats/textformat')
    if not symbol and not colorramp \
            and not labelsetting \
            and not legendpatchshape \
            and not symbol3d \
            and not textformat:
        raise ValidationError(_('Undefined style type. '
                                'Please register your style type.'))
    if symbol:
        _check_name_type_attribute(symbol)
    elif colorramp:
        _check_name_type_attribute(colorramp)
    elif labelsetting:
        _check_name_type_attribute(labelsetting)
    elif legendpatchshape:
        _check_name_type_attribute(legendpatchshape)
    elif symbol3d:
        _check_name_type_attribute(symbol3d)
    elif textformat:
        _check_name_type_attribute(textformat)
    xmlfile.seek(0)
    return True


def read_xml_style(xmlfile):
    """
    Parse XML file.

    The file should contains:
    - qgis_style tag in root
    - One of these following elements tag:
      - symbol
      - colorramp
      - labelsetting
      - legendpatchshape
      - symbol3d
    """

    try:
        tree = ET.parse(xmlfile)
    except ET.ParseError:
        raise ValidationError(_('Cannot parse the style file. '
                                'Please ensure your file is correct.'))
    root = tree.getroot()
    # find child elements
    symbol = root.find('./symbols/symbol')
    colorramp = root.find('./colorramps/colorramp')
    labelsetting = root.find('./labelsettings/labelsetting')
    legendpatchshape = root.find('./legendpatchshapes/legendpatchshape')
    symbol3d = root.find('./symbols3d/symbol3d')
    textformat = root.find('./textformats/textformat')

    if symbol:
        return {'name': symbol.get('name'),
                'type': symbol.get('type')}
    elif colorramp:
        return {'name': colorramp.get('name'),
                'type': 'colorramp'}
    elif labelsetting:
        return {'name': labelsetting.get('name'),
                'type': 'labelsetting'}
    elif legendpatchshape:
        return {'name': legendpatchshape.get('name'),
                'type': 'legendpatchshape'}
    elif symbol3d:
        return {'name': symbol3d.get('name'),
                'type': 'symbol3d'}
    elif textformat:
        return {'name': textformat.get('name'),
                'type': 'textformat'}
    else:
        return {'name': None, 'type': None}
