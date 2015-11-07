# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db.models import Q

from plugins.models import *

from django.core.exceptions import PermissionDenied

def export(request, **kwargs):
    if not request.user.is_superuser:
        raise PermissionDenied()
    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=plugins_users_list.csv'
    writer = csv.writer(response)
    for u in User.objects.all():
        writer.writerow([unicode(u.username).encode("utf-8"), u.email, unicode(u.get_full_name()).encode("utf-8"), u.date_joined])
    return response

def export_bad(request, **kwargs):
    """Plugin with missing metadata"""
    if not request.user.is_superuser:
        raise PermissionDenied()
    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=bad_plugins_users_list.csv'
    writer = csv.writer(response, dialect='excel-tab')
    writer.writerow(['Name', 'Author email', 'Maintainer email', 'Approved', 'Deprecated', 'Tracker', 'Repository', 'About'])
    for p in Plugin.approved_objects.filter(Q(about__isnull=True) | Q(about='') | Q(description__isnull=True) | Q(description='') |  Q(tracker__isnull=True) | Q(tracker='')):
        writer.writerow([unicode(p.name).encode("utf-8"), unicode(p.created_by.email).encode("utf-8"), p.email, p.approved, p.deprecated, p.tracker, p.repository, unicode(p.about).encode("utf-8")])
    return response


def export_plugin_maintainers(request, **kwargs):
    """Plugin maintainers"""
    if not request.user.is_superuser:
        raise PermissionDenied()
    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=plugin_maintainers.csv'
    writer = csv.writer(response, dialect='excel-tab')
    #writer.writerow(['email'])
    for u in User.objects.filter(plugins_created_by__isnull=False, email__isnull=False).exclude(email='').order_by('email').distinct():
        writer.writerow([unicode(u.email).encode("utf-8")])
    return response
