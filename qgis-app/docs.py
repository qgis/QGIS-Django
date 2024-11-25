from django.shortcuts import render
from django.utils.translation import gettext_lazy as _



def docs_publish(request):
    """
    Renders the docs_publish page
    """
    return render(
        request,
        "flatpages/docs_publish.html",
        {},
    )