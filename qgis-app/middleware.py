#-*- coding:utf-8 -*-
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
