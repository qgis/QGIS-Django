import os

from django.test import TestCase, override_settings
from django.conf import settings

from preferences import preferences
from unittest.mock import patch, MagicMock

from base.models.site_preferences import SitePreference
from plugins.tasks.generate_plugins_xml import generate_plugins_xml
from plugins.tasks.update_qgis_versions import update_qgis_versions


class TestPluginTask(TestCase):
    @patch.object(SitePreference.objects, 'first')
    @patch.object(SitePreference.objects, 'create')
    @patch('plugins.tasks.update_qgis_versions.get_qgis_versions')
    def test_update_qgis_versions(self, mock_get_qgis_versions, mock_create, mock_first):
        mock_create.return_value = MagicMock()
        mock_get_qgis_versions.return_value = ['3.16', '3.11', '3.12']
        site_preference = MagicMock()
        site_preference.qgis_versions = '3.16,3.17'
        mock_first.return_value = site_preference

        update_qgis_versions()

        self.assertEqual(site_preference.qgis_versions, '3.17,3.16,3.12,3.11')
        site_preference.save.assert_called_once()

    @patch.object(SitePreference.objects, 'first')
    @patch.object(SitePreference.objects, 'create')
    @patch('plugins.tasks.update_qgis_versions.get_qgis_versions')
    def test_update_qgis_versions_no_site_preference(self, mock_get_qgis_versions, mock_create, mock_first):
        mock_get_qgis_versions.return_value = ['3.16', '3.16', '3.16']
        mock_first.return_value = None
        mock_create.return_value = MagicMock()
        update_qgis_versions()
        mock_create.assert_called_once()

    @override_settings(DEFAULT_PLUGINS_SITE='http://test_plugins_site')
    @patch('requests.get')
    @patch('os.path.exists', return_value=False)
    @patch('os.mkdir')
    @patch('builtins.open', new_callable=MagicMock)
    def test_generate_plugins_xml(self, mock_open, mock_mkdir, mock_exists, mock_get):
        # Given
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<some xml content> QGIS Version 34002|Visit https://download.qgis.org to get your copy of version 3.40.2'
        mock_get.return_value = mock_response
        preferences.SitePreference.qgis_versions = '3.24,3.25'

        expected_folder_path = os.path.join(settings.MEDIA_ROOT, 'cached_xmls')

        # When
        generate_plugins_xml()

        # Then
        mock_mkdir.assert_called_once_with(expected_folder_path)
        expected_calls = [
            ((f'{settings.DEFAULT_PLUGINS_SITE}/plugins/plugins_new.xml?qgis=3.24',),),
            ((f'{settings.DEFAULT_PLUGINS_SITE}/plugins/plugins_new.xml?qgis=3.25',),)
        ]
        mock_get.assert_has_calls(expected_calls, any_order=True)
        mock_open.assert_any_call(os.path.join(expected_folder_path, 'plugins_3.24.xml'), 'w+')
        mock_open.assert_any_call(os.path.join(expected_folder_path, 'plugins_3.25.xml'), 'w+')

    @override_settings(DEFAULT_PLUGINS_SITE='http://test_plugins_site')
    @patch('requests.get')
    @patch('os.path.exists', return_value=False)
    @patch('os.mkdir')
    @patch('builtins.open', new_callable=MagicMock)
    def test_generate_plugins_xml_with_custom_site(self, mock_open, mock_mkdir, mock_exists, mock_get):
        # Given
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<some xml content>'
        mock_response.json.return_value = {'latest': {'version': '3.40'}, 'ltr': {'version': '3.40'}}
        mock_get.return_value = mock_response
        preferences.SitePreference.qgis_versions = '3.24,3.25'

        expected_folder_path = os.path.join(settings.MEDIA_ROOT, 'cached_xmls')

        # When
        generate_plugins_xml('http://custom_plugins_site')

        # Then
        mock_mkdir.assert_called_once_with(expected_folder_path)
        expected_calls = [
            (('http://custom_plugins_site/plugins/plugins_new.xml?qgis=3.24',),),
            (('http://custom_plugins_site/plugins/plugins_new.xml?qgis=3.25',),)
        ]
        mock_get.assert_has_calls(expected_calls, any_order=True)
        mock_open.assert_any_call(os.path.join(expected_folder_path, 'plugins_3.24.xml'), 'w+')
        mock_open.assert_any_call(os.path.join(expected_folder_path, 'plugins_3.25.xml'), 'w+')
