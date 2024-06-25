# -*- coding:utf-8 -*-
# myapp/middleware.py

from django.template import TemplateDoesNotExist
from django.shortcuts import render
from django.core.exceptions import RequestDataTooBig
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import logging
import sentry_sdk

"""
    QGIS-DJANGO - MIDDLEWARE

    Middlewares to fix behind proxy IP problems

    @license: GNU AGPL, see COPYING for details.
"""

logger = logging.getLogger(__name__)

def XForwardedForMiddleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        if "HTTP_X_FORWARDED_FOR" in request.META.keys():
            request.META["HTTP_X_PROXY_REMOTE_ADDR"] = request.META["REMOTE_ADDR"]
            parts = request.META["HTTP_X_FORWARDED_FOR"].split(",", 1)
            request.META["REMOTE_ADDR"] = parts[0]

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware

class HandleTemplateDoesNotExistMiddleware(MiddlewareMixin):
    """Handle missing templates"""
    def process_exception(self, request, exception):
        if isinstance(exception, TemplateDoesNotExist):
            return render(request, '404.html', status=404)
        return None

class HandleOSErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except OSError as e:
            logger.error("OSError occurred", exc_info=True)
            sentry_sdk.capture_exception(e)
            raise e
        return response
class HandleRequestDataTooBigMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except RequestDataTooBig:
            return JsonResponse({'error': 'Request data is too large. Please upload smaller files.'}, status=413)