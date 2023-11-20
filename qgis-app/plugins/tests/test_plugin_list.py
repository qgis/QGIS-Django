from django.test import TestCase
from django.urls import reverse
from ..models import Plugin

class PluginsListViewTestCase(TestCase):
    fixtures = [
        "fixtures/styles.json",
        "fixtures/auth.json",
        "fixtures/simplemenu.json",
        "fixtures/plugins.json",
    ]

    def setUp(self):
        pass

    def test_plugins_list_view(self):
        # Test the main plugins list view without any parameters
        response = self.client.get(reverse('approved_plugins'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'plugins/plugin_list.html')
        self.assertTrue('current_sort_query' in response.context)
        self.assertTrue('current_querystring' in response.context)
        self.assertTrue('per_page_list' in response.context)
        self.assertTrue('show_more_items_number' in response.context)

    def test_plugins_list_pagination(self):
        # Test the plugins list view with pagination
        response = self.client.get(reverse('approved_plugins'), {'per_page': 20})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('current_sort_query' in response.context)
        self.assertTrue('current_querystring' in response.context)
        self.assertTrue('per_page_list' in response.context)
        self.assertTrue('show_more_items_number' in response.context)

        show_more_items_number = response.context['show_more_items_number']
        self.assertEqual(show_more_items_number, 50)

        response = self.client.get(reverse('approved_plugins'), {'per_page': 110})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('current_sort_query' in response.context)
        self.assertTrue('current_querystring' in response.context)
        self.assertTrue('per_page_list' in response.context)
        self.assertTrue('show_more_items_number' in response.context)

        show_more_items_number = response.context['show_more_items_number']
        records_count = Plugin.approved_objects.count()
        self.assertEqual(show_more_items_number, records_count + 1)

    def test_plugins_list_sorting(self):
        # Test the plugins list view with sorting
        response = self.client.get(reverse('approved_plugins'), {'sort': 'name'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('current_sort_query' in response.context)
        self.assertTrue('current_querystring' in response.context)
        self.assertTrue('per_page_list' in response.context)
        self.assertTrue('show_more_items_number' in response.context)

