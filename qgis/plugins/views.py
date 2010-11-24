# Create your views here.

from plugins.models import *
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
# i18n
from django.utils.translation import ugettext_lazy as _
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib import messages

class PluginForm(ModelForm):
    class Meta:
        model = Plugin
        fields = ('title', 'name', 'description')


class PluginVersionForm(ModelForm):
    class Meta:
        model = PluginVersion
        exclude = ('created_by', 'plugin')


def plugin_create(request):
    """
    The form will automatically set published flag according to user permissions
    """
    if request.method == 'POST':
        form = PluginForm(request.POST, request.FILES)
        if form.is_valid():
            new_object = form.save(commit = False)
            new_object.created_by = request.user
            new_object.published = request.user.has_perm('plugins.can_publish')
            new_object.save()
            new_object.owners.add(request.user)
            msg = _("The Plugin was created successfully.")
            messages.success(request, msg, fail_silently=True)
            return HttpResponseRedirect(new_object.get_absolute_url())
    else:
        form = PluginForm()

    return render_to_response('plugins/plugin_form.html', { 'form' : form }, context_instance=RequestContext(request))

def plugin_delete(request, plugin_id):
    return

def plugin_update(request, plugin_id):
    return


def version_detail(request, plugin_id, version_id):
    return render_to_response('plugins/version_form.html', { 'form' : form }, context_instance=RequestContext(request))


def version_create(request, plugin_id):
    """
    The form will create versions according to permissions
    """
    plugin = get_object_or_404(Plugin, pk=plugin_id)
    if not request.user in plugin.owners.all():
        return render_to_response('plugins/version_permission_deny.html', { 'plugin' : plugin }, context_instance=RequestContext(request))

    if request.method == 'POST':
        version = PluginVersion(plugin = plugin, created_by = request.user)
        form = PluginVersionForm(request.POST, request.FILES, instance = version)
        if form.is_valid():
            new_object = form.save()
            msg = _("The Plugin Version was created successfully.")
            messages.success(request, msg, fail_silently=True)
            return HttpResponseRedirect(new_object.plugin.get_absolute_url())
    else:
        form = PluginVersionForm()

    return render_to_response('plugins/version_form.html', { 'form' : form, 'plugin' : plugin}, context_instance=RequestContext(request))

def version_delete(request, version_id):
    return

def version_update(request, version_id):
    return

