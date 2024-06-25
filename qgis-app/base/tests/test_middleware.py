from django.test import TestCase, RequestFactory
from django.template import TemplateDoesNotExist
from middleware import HandleTemplateDoesNotExistMiddleware
from django.urls import path
from django.urls import reverse

class HandleTemplateDoesNotExistMiddlewareTest(TestCase):
    fixtures = ["fixtures/simplemenu.json"]
    def setUp(self):
        # Mock get_response function
        self.factory = RequestFactory()
        self.get_response = lambda request: None
        self.middleware = HandleTemplateDoesNotExistMiddleware(self.get_response)

    def test_template_does_not_exist(self):
        url = '/planet/template'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(
            response, '404.html'
        )

    def test_no_template_error(self):
        request = self.factory.get('/planet/template')

        # Simulate a different exception
        response = self.middleware.process_exception(request, Exception("Some other error"))

        # Check that the middleware does not handle this
        self.assertIsNone(response)
