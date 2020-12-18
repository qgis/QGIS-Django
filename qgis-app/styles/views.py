import json
import logging
import os
import zipfile

from io import BytesIO

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core import serializers
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.views.decorators.cache import never_cache
from django.views.generic import (CreateView,
                                  DetailView,
                                  DeleteView,
                                  ListView,
                                  UpdateView)

from styles.models import Style, StyleType, StyleReview
from styles.forms import (StyleUploadForm,
                          StyleUpdateForm,
                          StyleReviewForm)

from styles.file_handler import read_xml_style

LICENSE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            "base", "license.txt")


def is_style_manager(user: User) -> bool:
    """Check if user is the members of Style Managers group."""

    return user.groups.filter(name="Style Managers").exists()


def check_styles_access(user: User, style: Style) -> bool:
    """Check if user is the creator of the style or is_staff."""

    return user.is_staff or style.creator == user or is_style_manager(user)


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


def style_notify(style: Style, created=True) -> None:
    """
    Email notification when a new style created.

    """
    recipients = [u.email for u in User.objects.filter(
        groups__name="Style Managers").exclude(email='')]

    if created:
        style_status = "created"
    else:
        style_status = "updated"

    if recipients:
        domain = Site.objects.get_current().domain
        mail_from = settings.DEFAULT_FROM_EMAIL

        send_mail_wrapper(
            _('A new style has been %s by %s.') % (style_status,
                                                   style.creator),
            _('\r\nStyle name is: %s\r\nStyle description is: %s\r\n'
              'Link: http://%s%s\r\n') % (style.name, style.description,
                                          domain, style.get_absolute_url()),
            mail_from,
            recipients,
            fail_silently=True)
        logging.debug('Sending email notification for %s style, '
                      'recipients:  %s' % (style.name, recipients))
    else:
        logging.warning('No recipients found for %s style notification'
                        % style.name)


def style_update_notify(style: Style, creator: User, staff: User) -> None:
    """
    Email notification system for approval styles
    """

    recipients = [u.email for u in User.objects.filter(
        groups__name="Style Managers").exclude(email='')]

    if creator.email:
        recipients += [creator.email]

    if style.approved:
        approval_state = 'approved'
    else:
        approval_state = 'rejected'

    review = style.stylereview_set.last()
    comment = review.comment

    if recipients:
        domain = Site.objects.get_current().domain
        mail_from = settings.DEFAULT_FROM_EMAIL
        send_mail_wrapper(
          _('Style %s %s notification.') % (style, approval_state),
          _('\r\nStyle %s %s by %s.\r\n%s\r\nLink: http://%s%s\r\n') % (
              style.name, approval_state, staff, comment, domain,
              style.get_absolute_url()),
          mail_from,
          recipients,
          fail_silently=True)
        logging.debug('Sending email %s notification for %s style, '
                      'recipients:  %s' % (approval_state, style, recipients))
    else:
        logging.warning('No recipients found for %s style %s notification' % (
            style, approval_state))


class StyleCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new style
    """

    form_class = StyleUploadForm
    template_name = 'styles/style_form.html'
    success_message = "Style was created successfully."

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.creator = self.request.user
        xml_parse = read_xml_style(obj.xml_file)
        if xml_parse:
            # check if name exists
            name_exist = Style.objects.filter(
                name__iexact=xml_parse['name']).exists()
            if name_exist:
                obj.name = "%s_%s" % (xml_parse['name'].title(),
                                      get_random_string(length=5))
            else:
                obj.name = xml_parse['name'].title()
            style_type = StyleType.objects.filter(
                symbol_type=xml_parse['type']).first()
            if not style_type:
                style_type = StyleType.objects.create(
                    symbol_type=xml_parse['type'],
                    name=xml_parse['type'].title(),
                    description="Automatically created from '"
                                "'an uploaded Style file")
            obj.style_type = style_type
        obj.save()
        style_notify(obj)
        msg = _("The Style has been successfully created.")
        messages.success(self.request, msg, 'success', fail_silently=True)
        return HttpResponseRedirect(reverse('style_detail',
                                            kwargs={'pk': obj.id}))


@method_decorator(never_cache, name='dispatch')
class StyleListView(ListView):
    """
    Style ListView
    """

    model = Style
    queryset = Style.approved_objects.all()
    context_object_name = 'style_list'
    template_name = 'styles/style_list.html'
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
            queries = q.split(" ")
            if queries:
                query_filter = Q()
                for query in queries:
                    query_filter &= (
                            Q(name__search=query)
                            | Q(description__search=query)
                            | Q(creator__username__search=query)
                            | Q(creator__first_name__search=query)
                            | Q(creator__last_name__search=query)
                    )
                qs = qs.filter(query_filter)
        order_by = self.request.GET.get('order_by', None)
        if order_by:
            qs = qs.order_by(order_by)
            if order_by == "-type":
                qs = qs.order_by('-style_type__name')
            elif order_by == "type":
                qs = qs.order_by('style_type__name')
        return qs


class StyleByTypeListView(StyleListView):
    context_object_name = 'style_list'

    def get_queryset(self):
        qs = super().get_queryset()
        style_type = self.kwargs['style_type']
        return qs.filter(style_type__name=style_type)

    def get_context_data(self, **kwargs):
        """
        Override get_context_data.

        Add 'title' to be displayed as page title
        """

        context = super(StyleByTypeListView, self).get_context_data(**kwargs)
        context['title'] = "%s Styles" % (self.kwargs['style_type'],)
        return context


class StyleUnapprovedListView(LoginRequiredMixin, StyleListView):
    context_object_name = 'style_list'
    queryset = Style.unapproved_objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_staff or is_style_manager(user):
            return qs
        return qs.filter(creator=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Waiting Review'
        return context


class StyleRequireActionListView(LoginRequiredMixin, StyleListView):
    context_object_name = 'style_list'
    queryset = Style.requireaction_objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_staff or is_style_manager(user):
            return qs
        return qs.filter(creator=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Requiring Update'
        return context


class StyleDetailView(DetailView):
    model = Style
    queryset = Style.objects.all()
    context_object_name = 'style_detail'

    def get_template_names(self):
        style = self.get_object()
        if not style.approved:
            return 'styles/style_review.html'
        return 'styles/style_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user = self.request.user
        if self.object.creator.first_name:
            creator = "%s %s" % (
                self.object.creator.first_name, self.object.creator.first_name)
        else:
            creator = self.object.creator.username
        context['creator'] = creator
        if self.object.stylereview_set.exists():
            if self.object.stylereview_set.last().reviewer.first_name:
                reviewer = "%s %s" % (
                    self.object.stylereview_set.last().reviewer.first_name,
                    self.object.stylereview_set.last().reviewer.last_name)
            else:
                reviewer = self.object.stylereview_set.last().reviewer \
                    .username
            context['reviewer'] = reviewer
        if user.is_staff or is_style_manager(user):
            context['form'] = StyleReviewForm()
        return context


class StyleUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update a style
    """

    model = Style
    form_class = StyleUpdateForm
    context_object_name = 'style'
    template_name = 'styles/style_update_form.html'

    def dispatch(self, request, *args, **kwargs):
        style = self.get_object()
        user = self.request.user
        if not check_styles_access(user, style):
            return render(request, 'styles/style_permission_deny.html',
                          {'style_name': style.name,
                           'context': "You cannot modify this style"})
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Update the style type according to the style XML file.
        """

        obj = form.save(commit=False)
        xml_parse = read_xml_style(obj.xml_file)
        if xml_parse:
            obj.style_type = StyleType.objects.filter(
                symbol_type=xml_parse['type']).first()
        obj.require_action = False
        obj.approved = False
        obj.save()
        style_notify(obj, created=False)
        msg = _("The Style has been successfully updated.")
        messages.success(self.request, msg, 'success', fail_silently=True)
        return HttpResponseRedirect(reverse_lazy('style_detail',
                                                 kwargs={'pk': obj.id}))


class StyleDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete a style.
    """

    model = Style
    context_object_file = 'style'
    success_url = reverse_lazy('style_list')
    slug_url_kwarg = 'name'
    slug_field = 'name'

    def dispatch(self, request, *args, **kwargs):
        style = self.get_object()
        user = self.request.user
        if not check_styles_access(user, style):
            return render(
                request, 'styles/style_permission_deny.html',
                {'style_name': style.name,
                 'context': "You cannot delete this style"})
        return super().dispatch(request, *args, **kwargs)


def style_download(request, pk):
    """
    Download style file and update download_count in Style model
    """

    style = get_object_or_404(Style, pk=pk)
    if not style.approved:
        if not check_styles_access(request.user, style):
            return render(
                request, 'styles/style_permission_deny.html',
                {'style_name': style.name,
                 'context': 'Download failed. This style is not approved'})
    else:
        style.increase_download_counter()
        style.save()

    # zip the style and license.txt
    filenames = (style.xml_file.file.name, LICENSE_FILE)
    in_memory_data = BytesIO()
    zf = zipfile.ZipFile(in_memory_data, "w")
    zip_subdir = '%s' % style.name

    for fpath in filenames:
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)
        zf.write(fpath, zip_path)

    zf.close()

    response = HttpResponse(
        in_memory_data.getvalue(), content_type="application/x-zip-compressed")
    response['Content-Disposition'] = 'attachment; filename=%s.zip' % (
        slugify(style.name, allow_unicode=True)
    )

    return response


def style_review(request, pk):
    """
    Submit a style review and send email notification
    """

    style = get_object_or_404(Style, pk=pk)
    if request.method == 'POST':
        form = StyleReviewForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            StyleReview.objects.create(
                style=style,
                reviewer=request.user,
                comment=data['comment'])
            if data['approval'] == 'approve':
                style.approved = True
                style.require_action = False
                msg = _("The Style has been approved.")
                messages.success(request, msg, 'success', fail_silently=True)
            else:
                style.approved = False
                style.require_action = True
                msg = _("The Style has been rejected.")
                messages.success(request, msg, 'error', fail_silently=True)
            style.save()
            # send email notification
            style_update_notify(style, style.creator, request.user)
    return HttpResponseRedirect(reverse('style_detail', kwargs={'pk': pk}))


@never_cache
def style_nav_content(request):
    """
    Provides data for sidebar style navigation
    """

    user = request.user
    all_styles = Style.approved_objects.count()
    waiting_review = 0
    require_action = 0
    if user.is_staff or is_style_manager(user):
        waiting_review = Style.unapproved_objects.distinct().count()
        require_action = Style.requireaction_objects.distinct().count()
    elif user.is_authenticated:
        waiting_review = Style.unapproved_objects.filter(
            creator=user).distinct().count()
        require_action = Style.requireaction_objects.filter(
            creator=user).distinct().count()
    number_style = {'all': all_styles,
                    'waiting_review': waiting_review,
                    'require_action': require_action}
    return JsonResponse(number_style, status=200)


@never_cache
def style_type_list(request):
    media_path = getattr(settings, 'MEDIA_URL')
    qs = StyleType.objects.all()
    qs_json = serializers.serialize('json', qs)
    qs_load = json.loads(qs_json)
    qs_add = {'qs': qs_load, 'icon_url': media_path}
    qs_json = json.dumps(qs_add)
    return HttpResponse(qs_json, content_type='application/json')
