import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.utils.crypto import get_random_string
from django.views.decorators.cache import never_cache
from django.views.generic import (CreateView,
                                  DetailView,
                                  DeleteView,
                                  ListView,
                                  UpdateView)

from styles.models import Style, StyleType, StyleReview
from styles.forms import StyleUploadForm, StyleUpdateForm, StyleReviewForm

from styles.file_handler import read_xml_style


def check_styles_access(user, style):
    """Check if user is the creator of the style or is_staff

    Parameters
    ----------
    user : User instance
        The user whom will be checked against the style
    style : Style instance

    Returns
    -------
    bool
        Return True if yser is_staff or user is style's creator
    """

    if user.is_staff or style.creator == user:
        return True
    return False


class StyleCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new style

    TODO:
    - check if style name is already exist, if it is,
    rename the style name = style name + author name
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
            name_exist = Style.objects.filter(name=xml_parse['name']).exists()
            if name_exist:
                obj.name = "%s_%s" % (xml_parse['name'].title(),
                                      get_random_string(length=5))
            else:
                obj.name = xml_parse['name'].title()
            style_type = StyleType.objects \
                .filter(symbol_type=xml_parse['type']).first()
            if not style_type:
                style_type = StyleType.objects.create(
                    symbol_type=xml_parse['type'],
                    name=xml_parse['type'].title(),
                    description="Automatically created from '"
                                "'an uploaded Style file")
            obj.style_type = style_type
        obj.save()
        msg = _("The Style has been successfully created.")
        messages.success(self.request, msg, 'success', fail_silently=True)
        return HttpResponseRedirect(reverse('style_detail',
                                            kwargs={'pk': obj.id}))


@method_decorator(never_cache, name='dispatch')
class StyleListView(ListView):
    """
    Style ListView.

    """
    model = Style
    queryset = Style.approved_objects.all()
    context_object_name = 'style_list'
    template_name = 'styles/style_list.html'
    paginate_by = settings.PAGINATION_DEFAULT_PAGINATION

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        order_by = self.request.GET.get('order_by', None)
        qs = super().get_queryset()
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


class StyleUnapprovedListView(LoginRequiredMixin, StyleListView):
    context_object_name = 'style_list'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Style.unapproved_objects.all()
        return Style.unapproved_objects.filter(creator=user).all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Waiting Review'
        return context


class StyleRequireActionListView(LoginRequiredMixin, StyleListView):
    context_object_name = 'style_list'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Style.requireaction_objects.all()
        return Style.requireaction_objects.filter(creator=user).all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Requiring Update'
        return context


class StyleDetailView(DetailView):
    model = Style
    queryset = Style.objects.all()
    context_object_name = 'style_detail'

    def dispatch(self, request, *args, **kwargs):
        style = self.get_object()
        user = self.request.user
        if not check_styles_access(user, style):
            return render(request, 'styles/style_permission_deny.html',
                {'style_name': style.name,
                 'context': "This style is in review"})
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        style = self.get_object()
        if not style.approved:
            return 'styles/style_review.html'
        return 'styles/style_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        if self.object.creator.first_name:
            creator = "%s %s" % (self.object.creator.first_name,
                self.object.creator.first_name)
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
        if self.request.user.is_staff:
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
            obj.style_type = StyleType.objects \
                .filter(symbol_type=xml_parse['type']).first()
        obj.require_action = False
        obj.save()
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
            return render(request, 'styles/style_permission_deny.html',
                {'style_name': style.name,
                 'context': "You cannot delete this style"})
        return super().dispatch(request, *args, **kwargs)


def style_download(request, pk):
    """
    Download style file and update download_count in Style model.

    TODO:
    - ensure download counter is increased when it hit.
    """
    style = get_object_or_404(Style, pk=pk)
    if not style.approved:
        if not check_styles_access(request.user, style):
            return render(request, 'styles/style_permission_deny.html',
                {'style_name': style.name,
                 'context': 'Download failed. This style is not approved'})
    else:
        style.increase_download_counter()
        style.save()
    with open(style.xml_file.file.name, 'rb') as style_file:
        file_content = style_file.read()
        response = HttpResponse(file_content, content_type='application/xml')
        response['Content-Disposition'] = 'attachment; filename=%s.xml' % (
            style.name
        )
        return response


def style_review(request, pk):
    """Review POST request"""
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
    return HttpResponseRedirect(reverse('style_detail', kwargs={'pk': pk}))


@never_cache
def style_nav_content(request):
    """Provides data for sidebar style navigation"""
    # TODO
    # get number of approval
    user = request.user
    all = Style.approved_objects.count()
    waiting_review = 0
    require_action = 0
    if user.is_staff:
        waiting_review = Style.unapproved_objects.distinct().count()
        require_action = Style.requireaction_objects.distinct().count()
    elif user.is_authenticated:
        waiting_review = Style.unapproved_objects.filter(creator=user) \
            .distinct().count()
        require_action = Style.requireaction_objects.filter(creator=user) \
            .distinct().count()
    number_style = {'all': all,
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
