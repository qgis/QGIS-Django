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

from models.forms import (ModelReviewForm,
                             ModelUpdateForm,
                             ModelUploadForm,)
from models.models import Model, ModelReview

LICENSE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            "base", "license.txt")


def is_resources_manager(user: User) -> bool:
    """Check if user is the members of Resources Managers group."""

    return user.groups.filter(name="Style Managers").exists()


def check_model_access(user: User, model: Model) -> bool:
    """Check if user is the creator of the Model or is_staff."""

    return user.is_staff or model.creator == user or is_resources_manager(user)


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


def model_notify(model: Model, created=True) -> None:
    """
    Email notification when a new Model created.
    """

    recipients = [u.email for u in User.objects.filter(
        groups__name="Style Managers").exclude(email='')]

    if created:
        model_status = "created"
    else:
        model_status = "updated"

    if recipients:
        domain = Site.objects.get_current().domain
        mail_from = settings.DEFAULT_FROM_EMAIL

        send_mail_wrapper(
            _('A new Model has been %s by %s.') % (model_status,
                                                   model.creator),
            _('\r\nModel name is: %s\r\nModel description is: %s\r\n'
              'Link: http://%s%s\r\n') % (model.name, model.description,
                                          domain, model.get_absolute_url()),
            mail_from,
            recipients,
            fail_silently=True)
        logging.debug('Sending email notification for %s Model, '
                      'recipients:  %s' % (model.name, recipients))
    else:
        logging.warning('No recipients found for %s Model notification'
                        % model.name)


def model_update_notify(model: Model, creator: User,
                               staff: User) -> None:
    """
    Email notification system when staff approved or rejected a Model
    """

    recipients = [u.email for u in User.objects.filter(
        groups__name="Style Managers").exclude(email='')]

    if creator.email:
        recipients += [creator.email]

    if model.approved:
        approval_state = 'approved'
    else:
        approval_state = 'rejected'

    review = model.modelreview_set.last()
    comment = review.comment

    if recipients:
        domain = Site.objects.get_current().domain
        mail_from = settings.DEFAULT_FROM_EMAIL
        send_mail_wrapper(
          _('Model %s %s notification.') % (model, approval_state),
          _('\r\nModel %s %s by %s.\r\n%s\r\nLink: http://%s%s\r\n') % (
              model.name, approval_state, staff, comment, domain,
              model.get_absolute_url()),
          mail_from,
          recipients,
          fail_silently=True)
        logging.debug('Sending email %s notification for %s Model, '
                      'recipients:  %s' % (approval_state, model, recipients))
    else:
        logging.warning('No recipients found for %s model %s notification' % (
            model, approval_state))


class ModelCreateView(LoginRequiredMixin, CreateView):
    """
    Upload a Model File
    """

    form_class = ModelUploadForm
    template_name = 'models/model_form.html'
    success_message = "Model was uploaded successfully."

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.creator = self.request.user
        obj.save()
        model_notify(obj)
        msg = _(self.success_message)
        messages.success(self.request, msg, 'success', fail_silently=True)
        return HttpResponseRedirect(reverse('model_detail',
                                            kwargs={'pk': obj.id}))


class ModelDetailView(DetailView):
    model = Model
    queryset = Model.objects.all()
    context_object_name = 'model_detail'

    def get_template_names(self):
        model = self.get_object()
        if not model.approved:
            return 'models/model_review.html'
        return 'models/model_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user = self.request.user
        context['creator'] = self.object.get_creator_name
        if self.object.modelreview_set.exists():
            if self.object.modelreview_set.last().reviewer.first_name:
                reviewer = "%s %s" % (
                    self.object.modelreview_set.last().reviewer.first_name,
                    self.object.modelreview_set.last().reviewer.last_name)
            else:
                reviewer = self.object.modelreview_set.last().reviewer \
                    .username
            context['reviewer'] = reviewer
        if user.is_staff or is_resources_manager(user):
            context['form'] = ModelReviewForm()
        return context


class ModelUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update a Model
    """

    model = Model
    form_class = ModelUpdateForm
    context_object_name = 'model'
    template_name = 'models/model_update_form.html'

    def dispatch(self, request, *args, **kwargs):
        model = self.get_object()
        user = self.request.user
        if not check_model_access(user, model):
            return render(request,
                          'models/model_permission_deny.html',
                          {'model_name': model.name,
                           'context': "You cannot delete this Model"})
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.require_action = False
        obj.approved = False
        obj.save()
        model_notify(obj, created=False)
        msg = _("The Model has been successfully updated.")
        messages.success(self.request, msg, 'success', fail_silently=True)
        return HttpResponseRedirect(reverse_lazy('model_detail',
                                                 kwargs={'pk': obj.id}))


@method_decorator(never_cache, name='dispatch')
class ModelListView(ListView):

    model = Model
    queryset = Model.approved_objects.all()
    context_object_name = 'model_list'
    template_name = 'models/model_list.html'
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


class ModelUnapprovedListView(LoginRequiredMixin, ModelListView):
    context_object_name = 'model_list'
    queryset = Model.unapproved_objects.all()

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


class ModelRequireActionListView(LoginRequiredMixin, ModelListView):
    context_object_name = 'model_list'
    queryset = Model.requireaction_objects.all()

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


class ModelDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete a Model.
    """

    model = Model
    context_object_file = 'model'
    success_url = reverse_lazy('model_list')

    def dispatch(self, request, *args, **kwargs):
        model = self.get_object()
        user = self.request.user
        if not check_model_access(user, model):
            return render(request,
                          'models/model_permission_deny.html',
                          {'model_name': model.name,
                           'context': "You cannot delete this Model"})
        return super().dispatch(request, *args, **kwargs)


def model_review(request, pk):
    """
    Submit a review and send email notification
    """

    model = get_object_or_404(Model, pk=pk)
    if request.method == 'POST':
        form = ModelReviewForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            ModelReview.objects.create(
                model=model,
                reviewer=request.user,
                comment=data['comment'])
            if data['approval'] == 'approve':
                model.approved = True
                model.require_action = False
                msg = _("The Model has been approved.")
                messages.success(request, msg, 'success', fail_silently=True)
            else:
                model.approved = False
                model.require_action = True
                msg = _("The Model has been rejected.")
                messages.success(request, msg, 'error', fail_silently=True)
            model.save()
            # send email notification
            model_update_notify(model, model.creator, request.user)
    return HttpResponseRedirect(reverse('model_detail',
                                        kwargs={'pk': pk}))


def model_download(request, pk):
    """
    Download Model and update its download_count value
    """

    model = get_object_or_404(Model, pk=pk)
    if not model.approved:
        if not check_model_access(request.user, model):
            return render(
                request, 'models/model_permission_deny.html',
                {'model_name': model.name,
                 'context': ('Download failed. '
                             'This Model is not approved')})
    else:
        model.increase_download_counter()
        model.save()

    # zip the model and license.txt
    filenames = (model.model_file.file.name, LICENSE_FILE)
    in_memory_data = BytesIO()
    zf = zipfile.ZipFile(in_memory_data, "w")
    zip_subdir = '%s' % model.name

    for fpath in filenames:
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)
        zf.write(fpath, zip_path)

    zf.close()

    response = HttpResponse(
        in_memory_data.getvalue(), content_type="application/x-zip-compressed")
    response['Content-Disposition'] = 'attachment; filename=%s.zip' % (
        slugify(model.name, allow_unicode=True)
    )

    return response


@never_cache
def model_nav_content(request):
    """
    Provides data for sidebar model navigation
    """

    user = request.user
    all_model = Model.approved_objects.count()
    waiting_review = 0
    require_action = 0
    if user.is_staff or is_resources_manager(user):
        waiting_review = Model.unapproved_objects.distinct().count()
        require_action = Model.requireaction_objects.distinct().count()
    elif user.is_authenticated:
        waiting_review = Model.unapproved_objects.filter(
            creator=user).distinct().count()
        require_action = Model.requireaction_objects.filter(
            creator=user).distinct().count()
    number_model = {'all': all_model,
                    'waiting_review': waiting_review,
                    'require_action': require_action}
    return JsonResponse(number_model, status=200)
