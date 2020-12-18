import logging
import os
import zipfile

from io import BytesIO

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
                                  UpdateView)

from geopackages.forms import (GeopackageReviewForm,
                             GeopackageUpdateForm,
                             GeopackageUploadForm,)
from geopackages.models import Geopackage, GeopackageReview

LICENSE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            "base", "license.txt")


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


class GeopackageCreateView(LoginRequiredMixin, CreateView):
    """
    Upload a GeoPackage File
    """

    form_class = GeopackageUploadForm
    template_name = 'geopackages/geopackage_form.html'
    success_message = "GeoPackage was uploaded successfully."

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.creator = self.request.user
        obj.save()
        geopackage_notify(obj)
        msg = _(self.success_message)
        messages.success(self.request, msg, 'success', fail_silently=True)
        return HttpResponseRedirect(reverse('geopackage_detail',
                                            kwargs={'pk': obj.id}))


class GeopackageDetailView(DetailView):
    model = Geopackage
    queryset = Geopackage.objects.all()
    context_object_name = 'geopackage_detail'

    def get_template_names(self):
        gpkg = self.get_object()
        if not gpkg.approved:
            return 'geopackages/geopackage_review.html'
        return 'geopackages/geopackage_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user = self.request.user
        context['creator'] = self.object.get_creator_name
        if self.object.geopackagereview_set.exists():
            if self.object.geopackagereview_set.last().reviewer.first_name:
                reviewer = "%s %s" % (
                    self.object.geopackagereview_set.last()
                        .reviewer.first_name,
                    self.object.geopackagereview_set.last().reviewer.last_name)
            else:
                reviewer = self.object.geopackagereview_set.last().reviewer \
                    .username
            context['reviewer'] = reviewer
        if user.is_staff or is_resources_manager(user):
            context['form'] = GeopackageReviewForm()
        return context


class GeopackageUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update a GeoPackage
    """

    model = Geopackage
    form_class = GeopackageUpdateForm
    context_object_name = 'geopackage'
    template_name = 'geopackages/geopackage_update_form.html'

    def dispatch(self, request, *args, **kwargs):
        gpkg = self.get_object()
        user = self.request.user
        if not check_geopackage_access(user, gpkg):
            return render(request,
                          'geopackages/geopackage_permission_deny.html',
                          {'geopackage_name': gpkg.name,
                           'context': "You cannot delete this GeoPackage"})
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.require_action = False
        obj.approved = False
        obj.save()
        geopackage_notify(obj, created=False)
        msg = _("The GeoPackage has been successfully updated.")
        messages.success(self.request, msg, 'success', fail_silently=True)
        return HttpResponseRedirect(reverse_lazy('geopackage_detail',
                                                 kwargs={'pk': obj.id}))


@method_decorator(never_cache, name='dispatch')
class GeopackageListView(ListView):

    model = Geopackage
    queryset = Geopackage.approved_objects.all()
    context_object_name = 'geopackage_list'
    template_name = 'geopackages/geopackage_list.html'
    paginate_by = settings.PAGINATION_DEFAULT_PAGINATION

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = self.get_queryset().count()
        context['order_by'] = self.request.GET.get('order_by', None)
        context['queries'] = self.request.GET.get('q', None)
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            qs = qs.annotate(
                search=(SearchVector('name')
                        + SearchVector('description')
                        + SearchVector('creator__username')
                        + SearchVector('creator__first_name')
                        + SearchVector('creator__last_name'))
            ).filter(search=q)
        order_by = self.request.GET.get('order_by', None)
        if order_by:
            qs = qs.order_by(order_by)
        return qs


class GeopackageUnapprovedListView(LoginRequiredMixin, GeopackageListView):
    context_object_name = 'geopackage_list'
    queryset = Geopackage.unapproved_objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_staff or is_resources_manager(user):
            return qs
        return qs.filter(creator=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Waiting Review'
        return context


class GeopackageRequireActionListView(LoginRequiredMixin, GeopackageListView):
    context_object_name = 'geopackage_list'
    queryset = Geopackage.requireaction_objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_staff or is_resources_manager(user):
            return qs
        return qs.filter(creator=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Requiring Update'
        return context


class GeopackageDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete a GeoPackage.
    """

    model = Geopackage
    context_object_file = 'geopackage'
    success_url = reverse_lazy('geopackage_list')

    def dispatch(self, request, *args, **kwargs):
        gpkg = self.get_object()
        user = self.request.user
        if not check_geopackage_access(user, gpkg):
            return render(request,
                          'geopackages/geopackage_permission_deny.html',
                          {'geopackage_name': gpkg.name,
                           'context': "You cannot delete this GeoPackage"})
        return super().dispatch(request, *args, **kwargs)


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
    filenames = (gpkg.gpkg_file.file.name, LICENSE_FILE)
    in_memory_data = BytesIO()
    zf = zipfile.ZipFile(in_memory_data, "w")
    zip_subdir = '%s' % gpkg.name

    for fpath in filenames:
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)
        zf.write(fpath, zip_path)

    zf.close()

    response = HttpResponse(
        in_memory_data.getvalue(), content_type="application/x-zip-compressed")
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
