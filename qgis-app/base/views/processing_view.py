import logging

from base.forms.processing_forms import ResourceBaseReviewForm
from base.license import zipped_with_license
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.postgres.search import SearchVector
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from django.views.generic.base import ContextMixin
from django.utils.encoding import escape_uri_path

GROUP_NAME = "Style Managers"


def is_resources_manager(user: User) -> bool:
    """Check if user is the members of Resources Managers group."""

    return user.groups.filter(name=GROUP_NAME).exists()


def check_resources_access(user: User, resource: models.base) -> bool:
    """Check if user is the creator of the resource or is_staff."""

    return user.is_staff or resource.creator == user or is_resources_manager(user)


def send_mail_wrapper(subject, message, mail_from, recipients, fail_silently=True):
    """
    Wrapping send_email function to send email only when not DEBUG.
    """

    if settings.DEBUG:
        logging.debug("Mail not sent (DEBUG=True)")
    else:
        send_mail(subject, message, mail_from, recipients, fail_silently)


def resource_notify(
    resource: models.base, created=True, resource_type: str = "Resource"
) -> None:
    """
    Email notification when a new resource created.
    """

    recipients = [
        u.email for u in User.objects.filter(groups__name=GROUP_NAME).exclude(email="")
    ]

    if created:
        resource_status = "created"
    else:
        resource_status = "updated"

    if recipients:
        domain = Site.objects.get_current().domain
        mail_from = settings.DEFAULT_FROM_EMAIL

        send_mail_wrapper(
            _("A new %s has been %s by %s.")
            % (resource_type, resource_status, resource.creator),
            _("\r\n%s name is: %s\r\n%s description is: %s\r\n" "Link: http://%s%s\r\n")
            % (
                resource_type,
                resource.name,
                resource_type,
                resource.description,
                domain,
                resource.get_absolute_url(),
            ),
            mail_from,
            recipients,
            fail_silently=True,
        )
        logging.debug(
            "Sending email notification for %s %s, "
            "recipients:  %s" % (resource.name, resource_type, recipients)
        )
    else:
        logging.warning(
            "No recipients found for %s %s notification"
            % (resource.name, resource_type)
        )


def resource_update_notify(
    resource: models.base, creator: User, staff: User, resource_type: str = "Resource"
) -> None:
    """
    Email notification system when staff approved or rejected a resource
    """

    recipients = [
        u.email for u in User.objects.filter(groups__name=GROUP_NAME).exclude(email="")
    ]

    if creator.email:
        recipients += [creator.email]

    if resource.approved:
        approval_state = "approved"
    else:
        approval_state = "rejected"

    review = resource.review_set.last()
    comment = review.comment

    if recipients:
        domain = Site.objects.get_current().domain
        mail_from = settings.DEFAULT_FROM_EMAIL
        send_mail_wrapper(
            _("%s %s %s notification.") % (resource_type, resource, approval_state),
            _("\r\n%s %s %s by %s.\r\n%s\r\nLink: http://%s%s\r\n")
            % (
                resource_type,
                resource.name,
                approval_state,
                staff,
                comment,
                domain,
                resource.get_absolute_url(),
            ),
            mail_from,
            recipients,
            fail_silently=True,
        )
        logging.debug(
            "Sending email %s notification for %s Resource, "
            "recipients:  %s" % (approval_state, resource, recipients)
        )
    else:
        logging.warning(
            "No recipients found for %s %s %s "
            "notification" % (resource, resource_type, approval_state)
        )


class ResourceBaseMixin(object):
    """
    Mixin class to provide standard settings for Resource.
    """

    resource_name = "Resource"
    resource_name_url_base = "resource"
    review_model = None


class ResourceSearchMixin(object):
    """
    Mixin class to provide search in ListView
    """

    def get_queryset_search(self, qs):
        q = self.request.GET.get("q")
        if q:
            qs = qs.annotate(
                search=(
                    SearchVector("name")
                    + SearchVector("description")
                    + SearchVector("creator__username")
                    + SearchVector("creator__first_name")
                    + SearchVector("creator__last_name")
                )
            ).filter(search=q)
        order_by = self.request.GET.get("order_by", None)
        if order_by:
            # for style sharing app, there is style_type column that doesn't
            # exist in deafult sharing app
            if order_by == "-type":
                qs = qs.order_by("-style_type__name")
            elif order_by == "type":
                qs = qs.order_by("style_type__name")
            else:
                qs = qs.order_by(order_by)
        return qs

    def get_queryset_search_and_is_creator(self, qs):
        qs = self.get_queryset_search(qs)
        user = self.request.user
        if user.is_staff or is_resources_manager(user):
            return qs
        return qs.filter(creator=user)


class ResourceBaseContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super(ResourceBaseContextMixin, self).get_context_data()

        # set the app page name
        context["resource_name"] = self.resource_name

        # url name rendered on template
        context["url_create"] = "%s_create" % self.resource_name_url_base
        context["url_list"] = "%s_list" % self.resource_name_url_base
        context["url_unapproved"] = "%s_unapproved" % (self.resource_name_url_base)
        context["url_require_action"] = "%s_require_action" % (
            self.resource_name_url_base
        )
        context["url_nav_content"] = "%s_nav_content" % (self.resource_name_url_base)

        context["url_download"] = "%s_download" % self.resource_name_url_base
        context["url_update"] = "%s_update" % self.resource_name_url_base
        context["url_delete"] = "%s_delete" % self.resource_name_url_base
        context["url_review"] = "%s_review" % self.resource_name_url_base
        context["url_detail"] = "%s_detail" % self.resource_name_url_base
        return context


@method_decorator(never_cache, name="dispatch")
class ResourceBaseCreateView(
    LoginRequiredMixin, ResourceBaseContextMixin, SuccessMessageMixin, CreateView
):
    """Upload a Resource File.

    We don't cache since there's a dynamic preference value on the template
    """

    template_name = "base/upload_form.html"
    is_1mb_limit_enable = True
    is_custom_license_agreement = False

    def form_valid(self, form):
        self.obj = form.save(commit=False)
        self.obj.creator = self.request.user
        self.obj.save()
        resource_notify(self.obj, resource_type=self.resource_name)
        msg = _(self.success_message)
        messages.success(self.request, msg, "success", fail_silently=True)
        return super(ResourceBaseCreateView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        return "%s was uploaded successfully." % self.resource_name

    def get_success_url(self):
        url_name = "%s_detail" % self.resource_name_url_base
        return reverse(url_name, kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["limit_1mb"] = self.is_1mb_limit_enable
        context["is_custom_license_agreement"] = self.is_custom_license_agreement
        return context


class ResourceBaseDetailView(ResourceBaseContextMixin, DetailView):
    """Base Class for Resource DetailView."""

    context_object_name = "object_detail"

    # js source files
    # e.g. js = ({'src': 'path/to/js/under/static/file.js', 'type': 'module'},)
    # attribute src is mandatory, type is optional
    js = ()

    # css source files
    # e.g css = ('path/to/css/file1.css', 'path/to/css/file1.css')
    css = ()

    is_3d_model = False
    license_template = "base/includes/license.html"

    def get_template_names(self):
        object = self.get_object()
        if not object.approved:
            return "base/review.html"
        return "base/detail.html"

    def get_queryset(self):
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user = self.request.user
        context["creator"] = self.object.get_creator_name
        context["js"] = self.js
        context["css"] = self.css
        context["is_3d_model"] = self.is_3d_model
        context["license_template"] = self.license_template
        if self.object.review_set.exists():
            if self.object.review_set.last().reviewer.first_name:
                reviewer = "%s %s" % (
                    self.object.review_set.last().reviewer.first_name,
                    self.object.review_set.last().reviewer.last_name,
                )
            else:
                reviewer = self.object.review_set.last().reviewer.username
            context["reviewer"] = reviewer
        if user.is_staff or is_resources_manager(user):
            context["form"] = ResourceBaseReviewForm(resource_name=self.resource_name)
            context["is_style_manager"] = is_resources_manager(user)
        if self.is_3d_model:
            context["url_viewer"] = "%s_viewer" % self.resource_name_url_base
        return context


class ResourceBaseUpdateView(LoginRequiredMixin, ResourceBaseContextMixin, UpdateView):
    """Update Resource"""

    context_object_name = "object"
    template_name = "base/update_form.html"
    is_1mb_limit_enable = True
    is_custom_license_agreement = False

    def dispatch(self, request, *args, **kwargs):
        object = self.get_object()
        user = self.request.user
        if not check_resources_access(user, object):
            url_name = "%s_list" % self.resource_name_url_base
            return HttpResponseRedirect(reverse(url_name))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.require_action = False
        obj.approved = False
        obj.save()
        resource_notify(obj, created=False, resource_type=self.resource_name)
        msg = _("The %s has been successfully updated." % self.resource_name)
        messages.success(self.request, msg, "success", fail_silently=True)
        url_name = "%s_detail" % self.resource_name_url_base
        return HttpResponseRedirect(reverse_lazy(url_name, kwargs={"pk": obj.id}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["limit_1mb"] = self.is_1mb_limit_enable
        context["is_custom_license_agreement"] = self.is_custom_license_agreement
        return context


@method_decorator(never_cache, name="dispatch")
class ResourceBaseListView(ResourceBaseContextMixin, ResourceSearchMixin, ListView):

    context_object_name = "object_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["count"] = self.get_queryset().count()
        context["order_by"] = self.request.GET.get("order_by", None)
        context["queries"] = self.request.GET.get("q", None)
        context["is_gallery"] = self.request.GET.get("is_gallery", None)
        return context

    def get_queryset(self):
        qs = self.model.approved_objects.all()
        qs = self.get_queryset_search(qs)
        return qs

    def get_template_names(self):
        context = self.get_context_data()
        is_gallery = context["is_gallery"]
        if is_gallery:
            self.paginate_by = settings.PAGINATION_DEFAULT_PAGINATION
            return "base/list_galery.html"
        else:
            return "base/list.html"

    def get_paginate_by(self, queryset):
        is_gallery = self.request.GET.get("is_gallery", None)
        if is_gallery:
            return settings.PAGINATION_DEFAULT_PAGINATION_HUB
        return settings.PAGINATION_DEFAULT_PAGINATION


class ResourceBaseUnapprovedListView(
    LoginRequiredMixin, ResourceBaseListView, ResourceSearchMixin
):
    def get_queryset(self):
        qs = self.model.unapproved_objects.all()
        qs = self.get_queryset_search_and_is_creator(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Waiting Review"
        return context


class ResourceBaseRequireActionListView(
    LoginRequiredMixin, ResourceBaseListView, ResourceSearchMixin
):
    def get_queryset(self):
        qs = self.model.requireaction_objects.all()
        qs = self.get_queryset_search_and_is_creator(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Requiring Update"
        return context


class ResourceBaseDeleteView(LoginRequiredMixin, ResourceBaseContextMixin, DeleteView):
    """
    Delete a resource instance.
    """

    context_object_file = "object"
    template_name = "base/confirm_delete.html"

    def dispatch(self, request, *args, **kwargs):
        object = self.get_object()
        user = self.request.user
        if not check_resources_access(user, object):
            url_name = "%s_list" % self.resource_name_url_base
            return HttpResponseRedirect(reverse(url_name))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        url_name = "%s_list" % self.resource_name_url_base
        return reverse_lazy(url_name)


class ResourceBaseReviewView(ResourceBaseMixin, View):
    form_class = ResourceBaseReviewForm
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        object = get_object_or_404(self.model, pk=self.kwargs["pk"])
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            self.review_model.objects.create(
                resource=object, reviewer=request.user, comment=data["comment"]
            )
            if data["approval"] == "approve":
                object.approved = True
                object.require_action = False
                msg = _("The %s has been approved." % self.resource_name)
                messages.success(request, msg, "success", fail_silently=True)
            else:
                object.approved = False
                object.require_action = True
                msg = _("The %s has been rejected." % self.resource_name)
                messages.success(request, msg, "error", fail_silently=True)
            object.save()
            # send email notification
            resource_update_notify(
                object, object.creator, request.user, self.resource_name
            )
        url_name = "%s_detail" % self.resource_name_url_base
        return HttpResponseRedirect(reverse(url_name, kwargs={"pk": self.kwargs["pk"]}))


class ResourceBaseDownload(ResourceBaseContextMixin, View):
    """Download resource files and zip it with license."""

    template_name = "base/permission_deny.html"

    def get(self, request, *args, **kwargs):
        object = get_object_or_404(self.model, pk=self.kwargs["pk"])
        if not object.approved:
            if not check_resources_access(self.request.user, object):
                context = super(ResourceBaseDownload, self).get_context_data()
                context["object_name"] = object.name
                context["context"] = (
                    "Download failed. This %s is " "not approved" % self.resource_name
                )
                return TemplateResponse(request, self.template_name, context)
        else:
            object.increase_download_counter()
            object.save()

        # zip the resource and license.txt
        zipfile = zipped_with_license(object.file.file.name, object.name)

        response = HttpResponse(
            zipfile.getvalue(), content_type="application/x-zip-compressed"
        )
        zip_name = slugify(object.name, allow_unicode=True)
        response["Content-Disposition"] = f"attachment; filename*=utf-8''{escape_uri_path(zip_name)}.zip"
        return response


@never_cache
def resource_nav_content(request, model):
    """
    Provides data for sidebar navigation
    """

    user = request.user
    all_object = model.approved_objects.count()
    waiting_review = 0
    require_action = 0
    if user.is_staff or is_resources_manager(user):
        waiting_review = model.unapproved_objects.distinct().count()
        require_action = model.requireaction_objects.distinct().count()
    elif user.is_authenticated:
        waiting_review = (
            model.unapproved_objects.filter(creator=user).distinct().count()
        )
        require_action = (
            model.requireaction_objects.filter(creator=user).distinct().count()
        )
    count_object = {
        "all": all_object,
        "waiting_review": waiting_review,
        "require_action": require_action,
    }
    return JsonResponse(count_object, status=200)
