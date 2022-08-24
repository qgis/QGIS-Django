"""
Validator for QLR file.
"""

import re
import xml.etree.ElementTree as ET

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def parse_qlr(xmlfile):
    xmlfile.seek(0)
    try:
        tree = ET.parse(xmlfile)
    except ET.ParseError:
        raise ValidationError(
            _("Cannot parse the qlr file. " "Please ensure your file is correct.")
        )
    return tree


def validator(xmlfile):
    tree = parse_qlr(xmlfile)
    root = tree.getroot()
    if not root or not root.tag == "qlr":
        raise ValidationError(
            _("Invalid root tag of qlr file. " "Please ensure your file is correct.")
        )
    return True


def get_url_datasource(xmlfile):
    tree = parse_qlr(xmlfile)
    root = tree.getroot()
    datasource = root.find("./maplayers/maplayer/datasource")
    rgx = r'(?<=url=)[\'"]?(.*?)[\'"&\s]*?$'
    try:
        url = re.findall(rgx, datasource.text)
    except TypeError:
        return None
    except AttributeError:
        return None
    result = url[0] if url else None
    return result


def get_provider(xmlfile):
    tree = parse_qlr(xmlfile)
    root = tree.getroot()
    provider = root.find("./maplayers/maplayer/provider")
    try:
        return provider.text
    except AttributeError:
        return None
