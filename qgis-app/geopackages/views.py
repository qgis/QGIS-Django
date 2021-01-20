import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.postgres.search import SearchVector
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.decorators.cache import never_cache
from django.views.generic import (CreateView,
                                  DetailView,
                                  DeleteView,
                                  ListView,
                                  UpdateView,
                                  View)

from base.license import zipped_with_license
from base.views.processing_view import (ResourceBaseCreateView,
                                        ResourceBaseDetailView,
                                        ResourceBaseUpdateView,
                                        ResourceBaseListView,
                                        ResourceBaseUnapprovedListView,
                                        ResourceBaseRequireActionListView,
                                        ResourceBaseDeleteView,
                                        ResourceBaseReviewView)

from geopackages.forms import (GeopackageReviewForm,
                               UpdateForm,
                               UploadForm,)
from geopackages.models import Geopackage, GeopackageReview


def is_resources_manager(user: User) -> bool:
    """Check if user is the members of Resources Managers group."""

    return user.groups.filter(name="Style Managers").exists()


def check_geopackage_access(user: User, gpkg: Geopackage) -> bool:
    """Check if user is the creator of the GeoPackage or is_staff."""

    return user.is_staff or gpkg.creator == user or is_resources_manager(user)


def send_mail_wrapper(subject,
                      message,
                      mail_from,
                      recipients,
                      fail_silently=True):
    """
    Wrapping send_email function to send email only when not DEBUG.
    """

    if settings.DEBUG:
        logging.debug("Mail not sent (DEBUG=True)")
    else:
        send_mail(subject,
                  message,
                  mail_from,
                  recipients,
                  fail_silently)


def geopackage_notify(gpkg: Geopackage, created=True) -> None:
    """
    Email notification when a new GeoPackage created.
    """

    recipients = [u.email for u in User.objects.filter(
        groups__name="Style Managers").exclude(email='')]

    if created:
        gpkg_status = "created"
    else:
        gpkg_status = "updated"

    if recipients:
        domain = Site.objects.get_current().domain
        mail_from = settings.DEFAULT_FROM_EMAIL

        send_mail_wrapper(
            _('A new GeoPackage has been %s by %s.') % (gpkg_status,
                                                   gpkg.creator),
            _('\r\nGeoPackage name is: %s\r\nGeoPackage description is: %s\r\n'
              'Link: http://%s%s\r\n') % (gpkg.name, gpkg.description,
                                          domain, gpkg.get_absolute_url()),
            mail_from,
            recipients,
            fail_silently=True)
        logging.debug('Sending email notification for %s GeoPackage, '
                      'recipients:  %s' % (gpkg.name, recipients))
    else:
        logging.warning('No recipients found for %s GeoPackage notification'
                        % gpkg.name)


def geopackage_update_notify(gpkg: Geopackage, creator: User,
                               staff: User) -> None:
    """
    Email notification system when staff approved or rejected a GeoPackage
    """

    recipients = [u.email for u in User.objects.filter(
        groups__name="Style Managers").exclude(email='')]

    if creator.email:
        recipients += [creator.email]

    if gpkg.approved:
        approval_state = 'approved'
    else:
        approval_state = 'rejected'

    review = gpkg.geopackagereview_set.last()
    comment = review.comment

    if recipients:
        domain = Site.objects.get_current().domain
        mail_from = settings.DEFAULT_FROM_EMAIL
        send_mail_wrapper(
          _('GeoPackage %s %s notification.') % (gpkg, approval_state),
          _('\r\nGeoPackage %s %s by %s.\r\n%s\r\nLink: http://%s%s\r\n') % (
              gpkg.name, approval_state, staff, comment, domain,
              gpkg.get_absolute_url()),
          mail_from,
          recipients,
          fail_silently=True)
        logging.debug('Sending email %s notification for %s GeoPackage, '
                      'recipients:  %s' % (approval_state, gpkg, recipients))
    else:
        logging.warning('No recipients found for %s geopackage %s '
                        'notification' % (gpkg, approval_state))

class ResourceMixin():
    """Mixin class for Geopackage."""

    model = Geopackage

    review_model = GeopackageReview

    # The resource_name will be displayed as the app name on web page
    resource_name = 'GeoPackage'

    # The url name in urls.py should start start with this value
    resource_name_url_base = 'geopackage'


class GeopackageCreateView(ResourceMixin, ResourceBaseCreateView):
    """Upload a GeoPackage File"""

    form_class = UploadForm


class GeopackageDetailView(ResourceMixin, ResourceBaseDetailView):

    pass


class GeopackageUpdateView(ResourceMixin, ResourceBaseUpdateView):
    """Update a GeoPackage"""

    form_class = UpdateForm


class GeopackageListView(ResourceMixin, ResourceBaseListView):
    pass


class GeopackageUnapprovedListView(ResourceMixin,
                                   ResourceBaseUnapprovedListView):
    pass


class GeopackageRequireActionListView(ResourceMixin,
                                      ResourceBaseRequireActionListView):
    """Geopackage Requires Action """


class GeopackageDeleteView(ResourceMixin, ResourceBaseDeleteView):
    """
    Delete a GeoPackage.
    """


def geopackage_review(request, pk):
    """
    Submit a review and send email notification
    """

    gpkg = get_object_or_404(Geopackage, pk=pk)
    if request.method == 'POST':
        form = GeopackageReviewForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            GeopackageReview.objects.create(
                geopackage=gpkg,
                reviewer=request.user,
                comment=data['comment'])
            if data['approval'] == 'approve':
                gpkg.approved = True
                gpkg.require_action = False
                msg = _("The GeoPackage has been approved.")
                messages.success(request, msg, 'success', fail_silently=True)
            else:
                gpkg.approved = False
                gpkg.require_action = True
                msg = _("The GeoPackage has been rejected.")
                messages.success(request, msg, 'error', fail_silently=True)
            gpkg.save()
            # send email notification
            geopackage_update_notify(gpkg, gpkg.creator, request.user)
    return HttpResponseRedirect(reverse('geopackage_detail',
                                        kwargs={'pk': pk}))

class GeopackageReviewView(ResourceMixin, ResourceBaseReviewView):
    pass


def geopackage_download(request, pk):
    """
    Download GeoPackage and update its download_count value
    """

    gpkg = get_object_or_404(Geopackage, pk=pk)
    if not gpkg.approved:
        if not check_geopackage_access(request.user, gpkg):
            return render(
                request, 'geopackages/geopackage_permission_deny.html',
                {'geopackage_name': gpkg.name,
                 'context': ('Download failed. '
                             'This GeoPackage is not approved')})
    else:
        gpkg.increase_download_counter()
        gpkg.save()

    # zip the geopackage and license.txt
    zipfile = zipped_with_license(gpkg.gpkg_file.file.name, gpkg.name)

    response = HttpResponse(
        zipfile.getvalue(), content_type="application/x-zip-compressed")
    response['Content-Disposition'] = 'attachment; filename=%s.zip' % (
        slugify(gpkg.name, allow_unicode=True)
    )

    return response


@never_cache
def geopackage_nav_content(request):
    """
    Provides data for sidebar geopackage navigation
    """

    user = request.user
    all_gpkg = Geopackage.approved_objects.count()
    waiting_review = 0
    require_action = 0
    if user.is_staff or is_resources_manager(user):
        waiting_review = Geopackage.unapproved_objects.distinct().count()
        require_action = Geopackage.requireaction_objects.distinct().count()
    elif user.is_authenticated:
        waiting_review = Geopackage.unapproved_objects.filter(
            creator=user).distinct().count()
        require_action = Geopackage.requireaction_objects.filter(
            creator=user).distinct().count()
    number_geopackage = {'all': all_gpkg,
                    'waiting_review': waiting_review,
                    'require_action': require_action}
    return JsonResponse(number_geopackage, status=200)
