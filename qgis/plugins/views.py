# Create your views here.
from django.db import transaction
from django.forms import ModelForm, ValidationError
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django import forms
from django.conf import settings

from plugins.models import *
from plugins.validator import validator

class PluginForm(ModelForm):
    class Meta:
        model = Plugin
        fields = ('name', 'description')


class PluginVersionForm(ModelForm):
    class Meta:
        model = PluginVersion
        exclude = ('created_by', 'plugin')

class PackageUploadForm(forms.Form):
    """
    Single step upload
    """
    package = forms.FileField(_('QGIS compressed plugin package'))
    def clean_package(self):
        cleaned_data    = self.cleaned_data
        package         = self.cleaned_data.get('package')
        try:
            self.cleaned_data.update(validator(package))
        except ValidationError, e:
            msg = unicode(_('File upload must be a valid QGIS Python plugin compressed archive.'))
            raise ValidationError("%s %s" % (msg, ','.join(e.messages)))

        if Plugin.objects.filter(name = self.cleaned_data['name']).count():
            raise ValidationError(_('A plugin with this name already exists.'))
        return package

def check_plugin_access(user, plugin):
    """
    Returns true if the user can modify the plugin:

        * is_staff
        * is owner

    """
    return user.is_staff or user in plugin.owners.all()

@login_required
def plugin_create(request):
    """
    The form will automatically set published flag according to user permissions.
    There is a more "automatic" alternative for creating new Plugins in a single step
    through package upload
    """
    if request.method == 'POST':
        form = PluginForm(request.POST, request.FILES)
        if form.is_valid():
            new_object = form.save(commit = False)
            new_object.created_by = request.user
            new_object.published = request.user.has_perm('plugins.can_publish')
            new_object.save()
            new_object.owners.add(request.user)
            msg = _("The Plugin has been successfully created.")
            messages.success(request, msg, fail_silently=True)
            return HttpResponseRedirect(new_object.get_absolute_url())
    else:
        form = PluginForm()

    return render_to_response('plugins/plugin_form.html', { 'form' : form , 'form_title' : _('New plugin')}, context_instance=RequestContext(request))


@login_required
def plugin_upload(request):
    """
    This is the "single step" way: uploads a package and creates
    a new Plugin with a new PluginVersion
    """
    if request.method == 'POST':
        form = PackageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            plugin_data = {
                'name'              : form.cleaned_data['name'],
                'description'       : form.cleaned_data['description'],
                'created_by'        : request.user,
                'published'         : request.user.has_perm('plugins.can_publish'),
            }
            new_plugin = Plugin(**plugin_data)
            new_plugin.save()
            new_plugin.owners.add(request.user)

            version_data =  {
                'plugin'            : new_plugin,
                'min_qg_version'    : form.cleaned_data['qgisMinimumVersion'],
                'version'           : form.cleaned_data['version'],
                'created_by'        : request.user,
                'package'           : form.cleaned_data['package']
            }
            new_version = PluginVersion(**version_data)
            new_version.save()
            msg = _("The Plugin has been successfully created.")
            messages.success(request, msg, fail_silently=True)
            return HttpResponseRedirect(new_plugin.get_absolute_url())
    else:
        form = PackageUploadForm()

    return render_to_response('plugins/plugin_upload.html', { 'form' : form }, context_instance=RequestContext(request))


@login_required
def plugin_delete(request, plugin_id):
    plugin = get_object_or_404(Plugin, pk=plugin_id)
    if not check_plugin_access(request.user, plugin):
        return render_to_response('plugins/plugin_permission_deny.html', {}, context_instance=RequestContext(request))
    if 'delete_confirm'  in request.POST:
        plugin.delete()
        msg = _("The Plugin has been successfully deleted.")
        messages.success(request, msg, fail_silently=True)
        return HttpResponseRedirect(reverse('plugins_list'))
    return render_to_response('plugins/plugin_delete_confirm.html', { 'plugin' : plugin }, context_instance=RequestContext(request))



@login_required
def plugin_update(request, plugin_id):
    """
    The form will automatically set published flag according to user permissions
    """
    plugin = get_object_or_404(Plugin, pk=plugin_id)
    if not check_plugin_access(request.user, plugin):
        return render_to_response('plugins/plugin_permission_deny.html', {}, context_instance=RequestContext(request))
    if request.method == 'POST':
        form = PluginForm(request.POST, request.FILES, instance = plugin)
        if form.is_valid():
            new_object = form.save(commit = False)
            if not request.user.has_perm('plugins.can_publish'):
                new_object.published = False
            new_object.modified_by = request.user
            new_object.save()
            if not new_object.owners.count():
                new_object.owners.add(request.user)
            msg = _("The Plugin has been successfully updated.")
            messages.success(request, msg, fail_silently=True)
            return HttpResponseRedirect(new_object.get_absolute_url())
    else:
        form = PluginForm(instance = plugin)

    return render_to_response('plugins/plugin_form.html', { 'form' : form , 'form_title' : _('Edit plugin')}, context_instance=RequestContext(request))


@login_required
def version_create(request, plugin_id):
    """
    The form will create versions according to permissions
    """
    plugin = get_object_or_404(Plugin, pk=plugin_id)
    if not check_plugin_access(request.user, plugin):
        return render_to_response('plugins/version_permission_deny.html', { 'plugin' : plugin }, context_instance=RequestContext(request))

    if request.method == 'POST':
        version = PluginVersion(plugin = plugin, created_by = request.user)
        form = PluginVersionForm(request.POST, request.FILES, instance = version)
        if form.is_valid():
            new_object = form.save()
            msg = _("The Plugin Version has been successfully created.")
            messages.success(request, msg, fail_silently=True)
            return HttpResponseRedirect(new_object.plugin.get_absolute_url())
    else:
        form = PluginVersionForm()

    return render_to_response('plugins/version_form.html', { 'form' : form, 'plugin' : plugin, 'form_title' : _('New version for plugin')}, context_instance=RequestContext(request))

@login_required
def version_delete(request, version_id):
    version = get_object_or_404(PluginVersion, pk=version_id)
    plugin = version.plugin
    if not user in plugin.owners.all():
        return render_to_response('plugins/version_permission_deny.html', {}, context_instance=RequestContext(request))
    if 'delete_confirm' in request.POST:
        version.delete()
        msg = _("The Plugin Version has been successfully deleted.")
        messages.success(request, msg, fail_silently=True)
        return HttpResponseRedirect(reverse('plugin_detail', args=(plugin.pk,)))
    return render_to_response('plugins/version_delete_confirm.html', { 'plugin' : plugin, 'version' : version }, context_instance=RequestContext(request))

@login_required
def version_update(request, version_id):
    """
    The form will create versions according to permissions
    """
    version = get_object_or_404(PluginVersion, pk=version_id)
    plugin = version.plugin
    if not check_plugin_access(request.user, plugin):
        return render_to_response('plugins/version_permission_deny.html', { 'plugin' : plugin }, context_instance=RequestContext(request))

    if request.method == 'POST':
        form = PluginVersionForm(request.POST, request.FILES, instance = version)
        if form.is_valid():
            new_object = form.save()
            msg = _("The Plugin Version has been successfully updated.")
            messages.success(request, msg, fail_silently=True)
            return HttpResponseRedirect(new_object.plugin.get_absolute_url())
    else:
        form = PluginVersionForm(instance = version)

    return render_to_response('plugins/version_form.html', { 'form' : form, 'plugin' : plugin, 'form_title' : _('Edit version for plugin')}, context_instance=RequestContext(request))

@login_required
def my_plugins(request):
    """
    Shows user's plugins (plugins where user is in owners)
    """
    object_list = Plugin.objects.filter(owners=request.user)
    return render_to_response('plugins/plugin_list.html', { 'object_list' : object_list, 'title' : _('My plugins')}, context_instance=RequestContext(request))

def version_download(request, version_id):
    """
    Update download counter(s)
    """
    version = get_object_or_404(PluginVersion, pk=version_id)
    version.downloads = version.downloads + 1
    version.save()
    plugin = version.plugin
    plugin.downloads = plugin.downloads + 1
    plugin.save()
    return HttpResponseRedirect(version.package.url)
