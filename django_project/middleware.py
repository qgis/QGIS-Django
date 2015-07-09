#-*- coding:utf-8 -*-
"""
    QGIS-DJANGO - MIDDLEWARE

    Middlewares to fix behind proxy IP problems

    @license: GNU AGPL, see COPYING for details.
"""


class XForwardedForMiddleware():
    """Sets the REMOTE_ADDR from HTTP_X_PROXY_REMOTE_ADDR"""
    def process_request(self, request):
        if request.META.has_key("HTTP_X_FORWARDED_FOR"):
            request.META["HTTP_X_PROXY_REMOTE_ADDR"] = request.META["REMOTE_ADDR"]
            parts = request.META["HTTP_X_FORWARDED_FOR"].split(",", 1)
            request.META["REMOTE_ADDR"] = parts[0]
