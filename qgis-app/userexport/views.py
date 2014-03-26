# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.models import User


from django.core.exceptions import PermissionDenied

def export(request, **kwargs):
    if not request.user.is_superuser:
        raise PermissionDenied()
    import csv
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=plugins_users_list.csv'
    writer = csv.writer(response)
    for u in User.objects.all():
        writer.writerow([unicode(u.username).encode("utf-8"), u.email, unicode(u.get_full_name()).encode("utf-8"), u.date_joined])
    return response
