import os
from tempfile import NamedTemporaryFile

from django.core.exceptions import ValidationError
from django.test import TestCase

from layerdefinitions.file_handler import (parse_qlr,
                                           validator,
                                           get_url_datasource,
                                           get_provider)

TESTFILE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'testfiles'))


class SetUpTest():
    """Setup for all test class."""
    def setUp(self):
        self.qlr_file = os.path.join(
            TESTFILE_DIR, "my-vapour-pressure.qlr")

class TestParseQlr(SetUpTest, TestCase):
    """Test the parse_qlr function."""

    def test_parse_qlr(self):
        with open(self.qlr_file) as f:
            self.assertTrue(parse_qlr(f))

    def test_parse_qlr_should_failed(self):
        tf = NamedTemporaryFile(mode='w+t', suffix=".qlr")
        tf.write("<broken xml")
        msg = "Cannot parse the qlr file. Please ensure your file is correct."
        with self.assertRaisesMessage(ValidationError, msg):
            parse_qlr(tf)


class TestValidator(SetUpTest, TestCase):
    """Test the validator function."""

    def test_validator_should_succeed(self):
        with open(self.qlr_file) as f:
            self.assertTrue(validator(f))

    def test_validator_should_failed(self):
        tf = NamedTemporaryFile(mode='w+t', suffix=".qlr")
        tf.write("<!DOCTYPE qgis-layer-definition><not_qlr></not_qlr>")
        msg = ("Invalid root tag of qlr file. "
               "Please ensure your file is correct.")
        with self.assertRaisesMessage(ValidationError, msg):
            validator(tf)


class TestGetUrlDatasource(SetUpTest, TestCase):
    """Test the get_url_datasource function."""

    def test_get_url_datasource_should_succeed(self):
        with open(self.qlr_file) as f:
            self.assertEqual(
                get_url_datasource(f),
                "https://maps.kartoza.com/geoserver/kartoza/wms"
            )

    def test_get_url_datasource_no_content_should_return_none(self):
        tf = NamedTemporaryFile(mode='w+t', suffix=".qlr")
        tf.write("<!DOCTYPE qgis-layer-definition>"
                 "<qlr><maplayers><maplayer><datasource>"
                 "</datasource></maplayer></maplayers></qlr>"
                 )
        self.assertIsNone(get_url_datasource(tf))

    def test_get_url_datasource_no_url_should_return_none(self):
        tf = NamedTemporaryFile(mode='w+t', suffix=".qlr")
        tf.write("<!DOCTYPE qgis-layer-definition>"
                 "<qlr><maplayers><maplayer><datasource>empty"
                 "</datasource></maplayer></maplayers></qlr>"
                 )
        self.assertIsNone(get_url_datasource(tf))


class TestGetProvider(SetUpTest, TestCase):
    """Test the get_url_datasource function."""

    def test_get_provider_should_succeed(self):
        with open(self.qlr_file) as f:
            self.assertEqual(get_provider(f), "wms")

    def test_get_provider_should_return_none(self):
        tf = NamedTemporaryFile(mode='w+t', suffix=".qlr")
        tf.write("<!DOCTYPE qgis-layer-definition>"
                 "<qlr><maplayers><maplayer><provider>"
                 "</provider></maplayer></maplayers></qlr>"
                 )
        self.assertIsNone(get_provider(tf))
