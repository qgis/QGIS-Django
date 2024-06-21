# -*- coding:utf-8 -*-
# myapp/middleware.py

from django.template import TemplateDoesNotExist
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

class HandleTemplateDoesNotExistMiddleware(MiddlewareMixin):
    """Handle missing templates"""
    def process_exception(self, request, exception):
        if isinstance(exception, TemplateDoesNotExist):
            return render(request, '404.html', status=404)
        return None


"""
    QGIS-DJANGO - MIDDLEWARE

    Middlewares to fix behind proxy IP problems

    @license: GNU AGPL, see COPYING for details.
"""


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
