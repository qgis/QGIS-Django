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
    writer = csv.writer(response)
    writer.writerow(['Name', 'Author email', 'Maintainer email', 'Approved', 'Deprecated'])
    for p in Plugin.approved_objects.filter(Q(about__isnull=True) | Q(about='') | Q(description__isnull=True) | Q(description='') |  Q(tracker__isnull=True) | Q(tracker='')):
        writer.writerow([unicode(p.name).encode("utf-8"), unicode(p.created_by.email).encode("utf-8"), p.email, p.approved, p.deprecated])
    return response
