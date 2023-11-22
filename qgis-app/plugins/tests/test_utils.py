from unittest.mock import patch, Mock
from django.test import TestCase
from plugins.utils import (
    get_qgis_versions,
    extract_version
)


class TestQGISGitHubReleases(TestCase):

    @patch('requests.get')
    def test_get_qgis_versions(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'tag_name': 'final_3_22_10', 'html_url': 'https://github.com/qgis/QGIS/releases/tag/final-3_22_10'},
            {'tag_name': 'beta_3_23_0', 'html_url': 'https://github.com/qgis/QGIS/releases/tag/beta-3_23_0'}
        ]
        mock_get.return_value = mock_response

        versions = get_qgis_versions()
        self.assertIn('3.22', versions)

    @patch('requests.get')
    def test_get_github_releases_failed_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with self.assertRaises(Exception) as context:
            get_qgis_versions()
        self.assertTrue('Request failed' in str(context.exception))

    def test_extract_version(self):
        self.assertEqual(extract_version('final-3.22.10'), '3.22')
        self.assertEqual(extract_version('beta-3.23.0'), '3.23')
        self.assertIsNone(extract_version('invalid-tag'))
