# Create your views here.
from django.core.exceptions import NON_FIELD_ERRORS
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from urlparse import urlsplit

from plugins.models import Plugin, PluginVersion
from plugins.forms import *

from django.core.mail import send_mail
from django.contrib.sites.models import Site

# Decorator
staff_required = user_passes_test(lambda u: u.is_staff)


def plugin_notify(plugin):
    """
    Sends a message to staff on new plugins
    """

    domain = Site.objects.get_current().domain
    mail_from = getattr(settings, 'MAIL_FROM_ADDRESS', None)
    if not mail_from:
        mail_from = 'qgis-plugins-no-reply@%s' % domain

    send_mail(
        _('A new plugin has been created by %s.') % plugin.created_by,
        _('\r\nPlugin name is: %s\r\nPlugin description is: %s\r\nLink: http://%s%s\r\n') % (plugin.name, plugin.description, domain, plugin.get_absolute_url()),
        mail_from,
        [u.email for u in User.objects.filter(is_staff = True, email__isnull = False)],
        fail_silently=True)


def check_plugin_access(user, plugin):
    """
    Returns true if the user can modify the plugin:

        * is_staff
        * is owner

    """
    return user.is_staff or user in plugin.editors


@login_required
def plugin_create(request):
    """
    The form will automatically set published flag according to user permissions.
    There is a more "automatic" alternative for creating new Plugins in a single step
    through package upload
    """
    if request.method == 'POST':
        form = PluginForm(request.POST, request.FILES)
        form.fields['owners'].queryset = User.objects.exclude(pk=request.user.pk)
        if form.is_valid():
            plugin = form.save(commit = False)
            plugin.created_by = request.user
            plugin.published  = request.user.has_perm('plugins.can_publish')
            plugin.save()
            plugin_notify(plugin)
            msg = _("The Plugin has been successfully created.")
            messages.success(request, msg, fail_silently=True)
            if not request.user.has_perm('plugins.can_publish'):
                msg = _("Your plugin is awaiting approval from a staff member and will be published as soon as possible.")
                messages.warning(request, msg, fail_silently=True)
            return HttpResponseRedirect(plugin.get_absolute_url())
    else:
        form = PluginForm()
        form.fields['owners'].queryset = User.objects.exclude(pk=request.user.pk)

    return render_to_response('plugins/plugin_form.html', { 'form' : form , 'form_title' : _('New plugin')}, context_instance=RequestContext(request))


@staff_required
def plugin_trust(request, plugin_id):
    """
    Assigns can_publish permission to the plugin creator
    """
    plugin = get_object_or_404(Plugin, pk=plugin_id)
    plugin.created_by.user_permissions.add(Permission.objects.get(codename='can_publish', content_type=ContentType.objects.get(name='plugin')))
    msg = _("The user %s is now a trusted user." % plugin.created_by)
    messages.success(request, msg, fail_silently=True)
    return HttpResponseRedirect(plugin.get_absolute_url())


@staff_required
def plugin_untrust(request, plugin_id):
    """
    Revokes can_publish permission to the plugin creator
    """
    plugin = get_object_or_404(Plugin, pk=plugin_id)
    plugin.created_by.user_permissions.remove(Permission.objects.get(codename='can_publish', content_type=ContentType.objects.get(name='plugin')))
    msg = _("The user %s is now an untrusted user." % plugin.created_by)
    messages.success(request, msg, fail_silently=True)
    return HttpResponseRedirect(plugin.get_absolute_url())


@staff_required
def plugin_set_featured(request, plugin_id):
    """
    Set as featured
    """
    plugin = get_object_or_404(Plugin, pk=plugin_id)
    plugin.featured = True
    plugin.save()
    msg = _("The plugin %s is now a marked as featured." % plugin)
    messages.success(request, msg, fail_silently=True)
    return HttpResponseRedirect(plugin.get_absolute_url())


@staff_required
def plugin_unset_featured(request, plugin_id):
    """
    Sets as not featured
    """
    plugin = get_object_or_404(Plugin, pk=plugin_id)
    plugin.featured = False
    plugin.save()
    msg = _("The plugin %s is not marked as featured anymore." % plugin)
    messages.success(request, msg, fail_silently=True)
    return HttpResponseRedirect(plugin.get_absolute_url())


@staff_required
def user_block(request, username):
    """
    Completely blocks a user
    """
    user = get_object_or_404(User, username=username)
    # Disable
    user.is_active = False
    user.save()
    msg = _("The user %s is now blocked." % user)
    messages.success(request, msg, fail_silently=True)
    redirect_to = reverse('published_plugins')
    try:
        redirect_to = urlsplit(request.REQUEST.get('HTTP_REFERER', None), 'http', False)[2]
    except:
        redirect_to = reverse('published_plugins')
    return HttpResponseRedirect(redirect_to)


@staff_required
def plugin_publish(request, plugin_id):
    """
    Publishes the plugin
    """
    plugin = get_object_or_404(Plugin, pk=plugin_id)
    plugin.published = True
    plugin.save()
    msg = _("The plugin is now published")
    messages.success(request, msg, fail_silently=True)
    return HttpResponseRedirect(plugin.get_absolute_url())


@staff_required
def plugin_unpublish(request, plugin_id):
    """
    Unpublishes the plugin
    """
    plugin = get_object_or_404(Plugin, pk=plugin_id)
    plugin.published = False
    plugin.save()
    msg = _("The plugin is now unpublished")
    messages.success(request, msg, fail_silently=True)
    return HttpResponseRedirect(plugin.get_absolute_url())


@login_required
def plugin_upload(request):
    """
    This is the "single step" way to create new plugins:
    uploads a package and creates a new Plugin with a new PluginVersion
    """
    if request.method == 'POST':
        form = PackageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                plugin_data = {
                    'name'              : form.cleaned_data['name'],
                    'package_name'      : form.cleaned_data['package_name'],
                    'description'       : form.cleaned_data['description'],
                    'created_by'        : request.user,
                    'published'         : request.user.has_perm('plugins.can_publish'),
                    'icon'              : form.cleaned_data['icon_file'],
                }
                new_plugin = Plugin(**plugin_data)
                new_plugin.save()
                plugin_notify(new_plugin)

                version_data =  {
                    'plugin'            : new_plugin,
                    'min_qg_version'    : form.cleaned_data['qgisMinimumVersion'],
                    'version'           : form.cleaned_data['version'],
                    'current'           : True,
                    'created_by'        : request.user,
                    'package'           : form.cleaned_data['package']
                }
                new_version = PluginVersion(**version_data)
                new_version.save()
                msg = _("The Plugin has been successfully created.")
                messages.success(request, msg, fail_silently=True)
                if not request.user.has_perm('plugins.can_publish'):
                    msg = _("Your plugin is awaiting approval from a staff member and will be published as soon as possible.")
                    messages.warning(request, msg, fail_silently=True)
            except (IntegrityError, ValidationError), e:
                messages.error(request, e, fail_silently=True)
                if not new_plugin.pk:
                    return render_to_response('plugins/plugin_upload.html', { 'form' : form }, context_instance=RequestContext(request))
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
        return HttpResponseRedirect(reverse('published_plugins'))
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
        form.fields['owners'].queryset = User.objects.exclude(pk=plugin.created_by.pk)
        if form.is_valid():
            new_object = form.save(commit = False)
            if not request.user.has_perm('plugins.can_publish'):
                new_object.published = False
            new_object.modified_by = request.user
            new_object.save()
            new_object.owners.clear()
            for o in form.cleaned_data['owners']:
                new_object.owners.add(o)
            msg = _("The Plugin has been successfully updated.")
            messages.success(request, msg, fail_silently=True)
            return HttpResponseRedirect(new_object.get_absolute_url())
    else:
        form = PluginForm(instance = plugin)
        form.fields['owners'].queryset = User.objects.exclude(pk=plugin.created_by.pk)

    return render_to_response('plugins/plugin_form.html', { 'form' : form , 'form_title' : _('Edit plugin')}, context_instance=RequestContext(request))


@login_required
def my_plugins(request):
    """
    Shows user's plugins (plugins where user is in owners or user is author)
    """
    object_list = Plugin.objects.filter(owners=request.user).distinct() | Plugin.objects.filter(created_by=request.user).distinct()
    return render_to_response('plugins/plugin_list.html', { 'object_list' : object_list, 'title' : _('My plugins')}, context_instance=RequestContext(request))

def user_plugins(request, username):
    """
    List published plugins created_by user
    """
    user = get_object_or_404(User, username=username)
    object_list = Plugin.published_objects.filter(created_by=user)
    return render_to_response('plugins/plugin_list.html', { 'object_list' : object_list, 'title' : _('Plugins from %s') % user }, context_instance=RequestContext(request))


@login_required
def version_create(request, plugin_id):
    """
    The form will create versions according to permissions,
    plugin name and description are updated according to the info
    contained in the package metadata
    """
    plugin = get_object_or_404(Plugin, pk=plugin_id)
    if not check_plugin_access(request.user, plugin):
        return render_to_response('plugins/version_permission_deny.html', { 'plugin' : plugin }, context_instance=RequestContext(request))

    version = PluginVersion(plugin = plugin, created_by = request.user)
    if request.method == 'POST':
        form = PluginVersionForm(request.POST, request.FILES, instance = version)
        if form.is_valid():
            new_object = form.save()
            msg = _("The Plugin Version has been successfully created.")
            messages.success(request, msg, fail_silently=True)
            if plugin.published and not request.user.has_perm('plugins.can_publish'):
                new_object.plugin.published = False
                new_object.plugin.save()
                messages.warning(request, _('You do not have publish permissions, plugin has been unpublished.'), fail_silently=True)
            # Update plugin
            plugin.icon = form.cleaned_data['icon_file']
            plugin.name = form.cleaned_data['name']
            plugin.description = form.cleaned_data['description']
            return HttpResponseRedirect(new_object.plugin.get_absolute_url())
    else:
        form = PluginVersionForm()

    return render_to_response('plugins/version_form.html', { 'form' : form, 'plugin' : plugin, 'form_title' : _('New version for plugin')}, context_instance=RequestContext(request))


@login_required
def version_update(request, version_id):
    """
    The form will update versions according to permissions
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
def version_delete(request, version_id):
    version = get_object_or_404(PluginVersion, pk=version_id)
    plugin = version.plugin
    if not check_plugin_access(request.user, plugin):
        return render_to_response('plugins/version_permission_deny.html', {}, context_instance=RequestContext(request))
    if 'delete_confirm' in request.POST:
        version.delete()
        msg = _("The Plugin Version has been successfully deleted.")
        messages.success(request, msg, fail_silently=True)
        return HttpResponseRedirect(reverse('plugin_detail', args=(plugin.pk,)))
    return render_to_response('plugins/version_delete_confirm.html', { 'plugin' : plugin, 'version' : version }, context_instance=RequestContext(request))


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


def version_detail(request, version_id):
    """
    Show version details
    """
    version = get_object_or_404(PluginVersion, pk=version_id)
    return render_to_response('plugins/version_detail.html', {'version' : version }, context_instance=RequestContext(request))
