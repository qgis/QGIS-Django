# Create your views here.
from django.core.exceptions import NON_FIELD_ERRORS
from django.db import IntegrityError
from django.db import connection
from django.db.models import Q
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.exceptions import FieldDoesNotExist
from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
#from sortable_listview import SortableListView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from plugins.models import Plugin, PluginVersion, vjust
from plugins.forms import *
from plugins.validator import PLUGIN_REQUIRED_METADATA

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie


from django.core.mail import send_mail
from django.contrib.sites.models import Site
import logging
import urllib
import copy

try:
    from urllib import urlencode
    from urlparse import urlparse, parse_qs
except ImportError:
    from urllib.parse import urlencode, urlparse, parse_qs

# Decorator
staff_required = user_passes_test(lambda u: u.is_staff)


def plugin_notify(plugin):
    """
    Sends a message to staff on new plugins
    """

    recipients = [u.email for u in User.objects.filter(is_staff=True, email__isnull=False).exclude(email='')]
    recipients.append(settings.QGIS_DEV_MAILING_LIST_ADDRESS)

    if recipients:
      domain = Site.objects.get_current().domain
      mail_from = settings.DEFAULT_FROM_EMAIL

      send_mail(
          unicode(_('A new plugin has been created by %s.') % plugin.created_by),
          unicode(_('\r\nPlugin name is: %s\r\nPlugin description is: %s\r\nLink: http://%s%s\r\n') % (plugin.name, plugin.description, domain, plugin.get_absolute_url())),
          mail_from,
          recipients,
          fail_silently=True)
      logging.debug('Sending email notification for %s plugin, recipients:  %s' % (plugin, recipients))
    else:
      logging.warning('No recipients found for %s plugin notification' % plugin)



def plugin_approve_notify(plugin, msg, user):
    """
    Sends a message when a plugin is approved or unapproved.
    """
    recipients = [u.email for u in plugin.editors if u.email]
    if settings.QGIS_DEV_MAILING_LIST_ADDRESS:
        recipients.append(settings.QGIS_DEV_MAILING_LIST_ADDRESS)
    if plugin.approved:
        approval_state = 'approval'
        approved_state = 'approved'
    else:
        approval_state = 'unapproval'
        approved_state = 'unapproved'

    if len(recipients):
        domain = Site.objects.get_current().domain
        mail_from = settings.DEFAULT_FROM_EMAIL
        logging.debug('Sending email %s notification for %s plugin, recipients:  %s' % (approval_state, plugin, recipients))
        send_mail(
          unicode(_('Plugin %s %s notification.') % (plugin, approval_state)),
          unicode(_('\r\nPlugin %s %s by %s.\r\n%s\r\nLink: http://%s%s\r\n') % (plugin.name, approval_state, user, msg, domain, plugin.get_absolute_url())),
          mail_from,
          recipients,
          fail_silently=True)
    else:
        logging.warning('No recipients found for %s plugin %s notification' % (plugin, approval_state))


def user_trust_notify(user):
    """
    Sends a message when an author is trusted or untrusted.
    """
    if user.is_staff:
        logging.debug('Skipping trust notification for staff user %s' % user)
    else:
        if user.email:
            recipients = [user.email]
            mail_from = settings.DEFAULT_FROM_EMAIL

            if user.has_perm('plugins.can_approve'):
                subject = unicode(_('User trust notification.'))
                message = unicode(_('\r\nYou can now approve your own plugins and the plugins you can edit.\r\n'))
            else:
                subject = unicode(_('User untrust notification.'))
                message = unicode(_('\r\nYou cannot approve any plugin.\r\n'))

            logging.debug('Sending email trust change notification to %s' % recipients)
            send_mail(
            subject,
            message,
            mail_from,
            recipients,
            fail_silently=True)
        else:
            logging.warning('No email found for %s user trust change notification' % user)

## Access control ##

def check_plugin_access(user, plugin):
    """
    Returns true if the user can modify the plugin:

        * is_staff
        * is owner

    """
    return user.is_staff or user in plugin.editors


def check_plugin_version_approval_rights(user, plugin):
    """
    Returns true if the user can approve the plugin version:

        * is_staff
        * is owner and is trusted

    """
    return user.is_staff or (user in plugin.editors and user.has_perm('plugins.can_approve'))


@login_required
def plugin_create(request):
    """
    The form will automatically set published flag according to user permissions.
    There is a more "automatic" alternative for creating new Plugins in a single step
    through package upload
    """
    if request.method == 'POST':
        form = PluginForm(request.POST, request.FILES)
        form.fields['owners'].queryset = User.objects.exclude(pk=request.user.pk).order_by('username')
        if form.is_valid():
            plugin = form.save(commit = False)
            plugin.created_by = request.user
            plugin.save()
            plugin_notify(plugin)
            msg = _("The Plugin has been successfully created.")
            messages.success(request, msg, fail_silently=True)
            return HttpResponseRedirect(plugin.get_absolute_url())
    else:
        form = PluginForm()
        form.fields['owners'].queryset = User.objects.exclude(pk=request.user.pk).order_by('username')

    return render_to_response('plugins/plugin_form.html', { 'form' : form , 'form_title' : _('New plugin')}, context_instance=RequestContext(request))



@staff_required
@require_POST
def plugin_set_featured(request, package_name):
    """
    Set as featured
    """
    plugin = get_object_or_404(Plugin, package_name=package_name)
    plugin.featured = True
    plugin.save()
    msg = _("The plugin %s is now a marked as featured." % plugin)
    messages.success(request, msg, fail_silently=True)
    return HttpResponseRedirect(plugin.get_absolute_url())


@staff_required
@require_POST
def plugin_unset_featured(request, package_name):
    """
    Sets as not featured
    """
    plugin = get_object_or_404(Plugin, package_name=package_name)
    plugin.featured = False
    plugin.save()
    msg = _("The plugin %s is not marked as featured anymore." % plugin)
    messages.success(request, msg, fail_silently=True)
    return HttpResponseRedirect(plugin.get_absolute_url())


@login_required
def plugin_upload(request):
    """
    This is the "single step" way to create new plugins:
    uploads a package and creates a new Plugin with a new PluginVersion
    can also update an existing plugin
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
                    'author'            : form.cleaned_data['author'],
                    'email'             : form.cleaned_data['email'],
                    'created_by'        : request.user,
                    'icon'              : form.cleaned_data['icon_file'],
                }

                # Gets existing plugin
                try:
                    plugin = Plugin.objects.get(package_name=plugin_data['package_name'])
                    if not check_plugin_access(request.user, plugin):
                        return render_to_response('plugins/plugin_permission_deny.html', {}, context_instance=RequestContext(request))
                    # Apply new values
                    plugin.name         = plugin_data['name']
                    plugin.description  = plugin_data['description']
                    plugin.author       = plugin_data['author']
                    plugin.email        = plugin_data['email']
                    is_new = False
                except Plugin.DoesNotExist:
                    plugin = Plugin(**plugin_data)
                    is_new = True

                # Check icon, don't change if not valid
                if plugin_data['icon']:
                    plugin.icon         = plugin_data['icon']

                # Server is optional
                plugin.server = form.cleaned_data.get('server', False)

                # Other optional fields
                warnings = []

                if form.cleaned_data.get('homepage'):
                    plugin.homepage = form.cleaned_data.get('homepage')
                elif not plugin.homepage:
                    warnings.append(_('<strong>homepage</strong> field is empty, this field is not required but is recommended, please consider adding it to metadata.'))
                if form.cleaned_data.get('tracker'):
                    plugin.tracker = form.cleaned_data.get('tracker')
                elif not plugin.tracker:
                    raise ValidationError(_('"tracker" metadata is required! Please add it to <code>metadata.txt</code>.'))
                if form.cleaned_data.get('repository'):
                    plugin.repository = form.cleaned_data.get('repository')
                elif not plugin.repository:
                    raise ValidationError(_('"repository" metadata is required! Please add it to <code>metadata.txt</code>.'))
                if form.cleaned_data.get('about'):
                    plugin.about = form.cleaned_data.get('about')
                elif not plugin.about:
                    raise ValidationError(_('"about" metadata is required! Please add it to <code>metadata.txt</code>.'))


                # Save main Plugin object
                plugin.save()

                if is_new:
                    plugin_notify(plugin)

                # Takes care of tags
                if form.cleaned_data.get('tags'):
                    plugin.tags.set(*[t.strip().lower() for t in form.cleaned_data.get('tags').split(',')])

                version_data =  {
                    'plugin'            : plugin,
                    'min_qg_version'    : form.cleaned_data.get('qgisMinimumVersion'),
                    'max_qg_version'    : form.cleaned_data.get('qgisMaximumVersion'),
                    'version'           : form.cleaned_data.get('version'),
                    'created_by'        : request.user,
                    'package'           : form.cleaned_data.get('package'),
                    'approved'          : request.user.has_perm('plugins.can_approve') or plugin.approved,
                    'experimental'      : form.cleaned_data.get('experimental'),
                    'changelog'         : form.cleaned_data.get('changelog', ''),
                    'external_deps'     : form.cleaned_data.get('external_deps', ''),
                }

                new_version = PluginVersion(**version_data)
                new_version.save()
                msg = _("The Plugin has been successfully created.")
                messages.success(request, msg, fail_silently=True)
                if not request.user.has_perm('plugins.can_approve'):
                    msg = _("Your plugin is awaiting approval from a staff member and will be approved as soon as possible.")
                    warnings.append(msg)
                if not  form.cleaned_data.get('metadata_source') == 'metadata.txt':
                    msg = _("Your plugin does not contain a metadata.txt file, metadata have been read from the __init__.py file. This is deprecated and its support will eventually cease.")
                    warnings.append(msg)

                # Grouped messages:
                if warnings:
                    messages.warning(request, _('<p><strong>Warnings:</strong></p>') + '\n'.join(["<p>%s</p>" % unicode(w) for w in warnings]), fail_silently=True)


            except (IntegrityError, ValidationError, DjangoUnicodeDecodeError), e:
                connection.close()
                messages.error(request, e, fail_silently=True)
                if not plugin.pk:
                    return render_to_response('plugins/plugin_upload.html', { 'form' : form }, context_instance=RequestContext(request))
            return HttpResponseRedirect(plugin.get_absolute_url())
    else:
        form = PackageUploadForm()

    return render_to_response('plugins/plugin_upload.html', { 'form' : form }, context_instance=RequestContext(request))



class PluginDetailView(DetailView):
    model = Plugin
    queryset = Plugin.objects.all()

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(PluginDetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        plugin = kwargs.get('object')
        context = super(PluginDetailView, self).get_context_data(**kwargs)
        # Warnings for owners
        if check_plugin_access(self.request.user, plugin):
            if not plugin.homepage:
                msg = _('<strong>homepage</strong> metadata is missing, this is not required but recommended. Please consider adding "homepage" to  <code>metadata.txt</code>.')
                messages.warning(self.request, msg, fail_silently=True)
            for md in set(PLUGIN_REQUIRED_METADATA)  - set(('version', 'qgisMinimumVersion')):
                if not getattr(plugin, md, None):
                    msg = _('<strong>%s</strong> metadata is missing, this metadata entry is <strong>required</strong>. Please add <strong>%s</strong> to <code>metadata.txt</code>.')% (md, md)
                    messages.error(self.request, msg, fail_silently=True)
        context.update({
            'rating': int(plugin.rating.get_rating()),
            'votes': plugin.rating.votes,
        })
        return context


@login_required
def plugin_delete(request, package_name):
    plugin = get_object_or_404(Plugin, package_name=package_name)
    if not check_plugin_access(request.user, plugin):
        return render_to_response('plugins/plugin_permission_deny.html', {}, context_instance=RequestContext(request))
    if 'delete_confirm' in request.POST:
        plugin.delete()
        msg = _("The Plugin has been successfully deleted.")
        messages.success(request, msg, fail_silently=True)
        return HttpResponseRedirect(reverse('approved_plugins'))
    return render_to_response('plugins/plugin_delete_confirm.html', { 'plugin' : plugin }, context_instance=RequestContext(request))


def _check_optional_metadata(form, request):
    """
    Checks for the presence of optional metadata
    """
    if not form.cleaned_data.get('homepage'):
        messages.warning(request, _('Homepage field is empty, this field is not required but is recommended, please consider adding it to  <code>metadata.txt</code>.'), fail_silently=True)


@login_required
def plugin_update(request, package_name):
    """
    Plugin update form
    """
    plugin = get_object_or_404(Plugin, package_name=package_name)
    if not check_plugin_access(request.user, plugin):
        return render_to_response('plugins/plugin_permission_deny.html', {}, context_instance=RequestContext(request))
    if request.method == 'POST':
        form = PluginForm(request.POST, request.FILES, instance=plugin)
        form.fields['owners'].queryset = User.objects.exclude(pk=plugin.created_by.pk).order_by('username')
        if form.is_valid():
            new_object = form.save(commit=False)
            new_object.modified_by = request.user
            new_object.save()
            # Without this next line the tags won't be saved.
            form.save_m2m()
            new_object.owners.clear()
            for o in form.cleaned_data['owners']:
                new_object.owners.add(o)
            msg = _("The Plugin has been successfully updated.")
            messages.success(request, msg, fail_silently=True)

            # Checks for optional metadata
            _check_optional_metadata(form, request)

            return HttpResponseRedirect(new_object.get_absolute_url())
    else:
        form = PluginForm(instance = plugin)
        form.fields['owners'].queryset = User.objects.exclude(pk=plugin.created_by.pk).order_by('username')

    return render_to_response('plugins/plugin_form.html', { 'form' : form , 'form_title' : _('Edit plugin'), 'plugin' : plugin}, context_instance=RequestContext(request))



class PluginsList(ListView):
    model = Plugin
    queryset = Plugin.approved_objects.all()
    title =  _('All plugins')
    additional_context = {}
    paginate_by = settings.PAGINATION_DEFAULT_PAGINATION

    def get_paginate_by(self, queryset):
        """
        Paginate by specified value in querystring, or use default class property value.
        """
        try:
            paginate_by = int(self.request.GET.get('per_page', self.paginate_by))
        except ValueError:
            paginate_by = self.paginate_by
        return paginate_by

    def get_queryset(self):
        qs = super(PluginsList, self).get_queryset()
        sort_by = self.request.GET.get('sort', None)
        if sort_by:
            if sort_by[0] == '-':
                _sort_by = sort_by[1:]
            else:
                _sort_by = sort_by
            try:
                # Average vote is not a field!
                _sort_by == 'average_vote' or self.model._meta.get_field(_sort_by)
                qs = qs.order_by(sort_by)
            except FieldDoesNotExist:
                pass
        return qs

    def get_context_data(self, **kwargs):
        context = super(PluginsList, self).get_context_data(**kwargs)
        context.update({
            'title': self.title,
        })
        context.update(self.additional_context)
        context['current_sort_query'] = self.get_sortstring()
        context['current_querystring'] = self.get_querystring()
        return context


    def get_sortstring(self):
        if self.request.GET.get('sort', None):
            return 'sort=%s' % self.request.GET.get('sort')
        return ''


    def get_querystring(self):
        """
        Clean existing query string (GET parameters) by removing
        arguments that we don't want to preserve (sort parameter, 'page')
        """
        to_remove = ['page', 'sort']
        query_string = urlparse(self.request.get_full_path()).query
        query_dict = parse_qs(query_string)
        for arg in to_remove:
            if arg in query_dict:
                del query_dict[arg]
        clean_query_string = urlencode(query_dict, doseq=True)
        return clean_query_string


class MyPluginsList(PluginsList):

    def get_queryset(self):
        return Plugin.base_objects.filter(owners=self.request.user).distinct()\
         | Plugin.objects.filter(created_by=self.request.user).distinct()


class UserPluginsList(PluginsList):

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return Plugin.approved_objects.filter(created_by=user)


class AuthorPluginsList(PluginsList):

    def get_queryset(self):
        return Plugin.approved_objects.filter(author=urllib.unquote(self.kwargs['author']))

    def get_context_data(self, **kwargs):
        context = super(AuthorPluginsList, self).get_context_data(**kwargs)
        context.update({
            'title' : _('Plugins by %s') % urllib.unquote(self.kwargs['author']),
        })
        return context



class UserDetailsPluginsList(PluginsList):
    """
    List plugins created_by OR owned by user
    """
    template_name = 'plugins/user.html'
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return Plugin.approved_objects.filter(Q(created_by=user) | Q(owners=user))

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs['username'])
        user_is_trusted = user.has_perm('plugins.can_approve')
        context = super(UserDetailsPluginsList, self).get_context_data(**kwargs)
        context.update({
            'title' : _('Plugins from %s') % user,
            'user_is_trusted' : user_is_trusted,
            'plugin_user': user,
        })
        return context


class TagsPluginsList(PluginsList):

    def get_queryset(self):
        return Plugin.approved_objects.filter(tagged_items__tag__slug=urllib.unquote(self.kwargs['tags']))

    def get_context_data(self, **kwargs):
        context = super(TagsPluginsList, self).get_context_data(**kwargs)
        context.update({
            'title' : _('Plugins tagged with: %s') % urllib.unquote(self.kwargs['tags']),
        })
        return context


@login_required
@require_POST
def plugin_manage(request, package_name):
    """
    Entry point for the plugin management functions
    """
    if request.POST.get('set_featured'):
        return plugin_set_featured(request, package_name)
    if request.POST.get('unset_featured'):
        return plugin_unset_featured(request, package_name)
    if request.POST.get('delete'):
        return plugin_delete(request, package_name)

    return HttpResponseRedirect(reverse('user_details', args=[username]))



###############################################

# User management functions

###############################################


@staff_required
@require_POST
def user_block(request, username):
    """
    Completely blocks a user
    """
    user = get_object_or_404(User, username=username, is_staff=False)
    # Disable
    user.is_active = False
    user.save()
    msg = unicode(_("The user %s is now blocked." % user))
    messages.success(request, msg, fail_silently=True)
    return HttpResponseRedirect(reverse('user_details', args=[user.username]))


@staff_required
@require_POST
def user_unblock(request, username):
    """
    unblocks a user
    """
    user = get_object_or_404(User, username=username, is_staff=False)
    # Enable
    user.is_active = True
    user.save()
    msg = unicode(_("The user %s is now unblocked." % user))
    messages.success(request, msg, fail_silently=True)
    return HttpResponseRedirect(reverse('user_details', args=[user.username]))


@staff_required
@require_POST
def user_trust(request, username):
    """
    Assigns can_approve permission to the plugin creator
    """
    user = get_object_or_404(User, username=username)
    user.user_permissions.add(Permission.objects.get(codename='can_approve', content_type=ContentType.objects.get(app_label="plugins", model='plugin')))
    msg = unicode(_("The user %s is now a trusted user." % user))
    messages.success(request, msg, fail_silently=True)
    user_trust_notify(user)
    return HttpResponseRedirect(reverse('user_details', args=[user.username]))


@staff_required
@require_POST
def user_untrust(request, username):
    """
    Revokes can_approve permission to the plugin creator
    """
    user = get_object_or_404(User, username=username)
    user.user_permissions.remove(Permission.objects.get(codename='can_approve', content_type=ContentType.objects.get(app_label="plugins", model='plugin')))
    msg = unicode(_("The user %s is now an untrusted user." % user))
    messages.success(request, msg, fail_silently=True)
    user_trust_notify(user)
    return HttpResponseRedirect(reverse('user_details', args=[user.username]))


@staff_required
@require_POST
def user_permissions_manage(request, username):
    """
    Entry point for the user management functions
    """
    if request.POST.get('user_block'):
        return user_block(request, username)
    if request.POST.get('user_unblock'):
        return user_unblock(request, username)
    if request.POST.get('user_trust'):
        return user_trust(request, username)
    if request.POST.get('user_untrust'):
        return user_untrust(request, username)

    return HttpResponseRedirect(reverse('user_details', args=[username]))


###############################################

# Version management functions

###############################################


def _main_plugin_update(request, plugin, form):
    """
    Updates the main plugin object from version metadata
    """
    # Update plugin from metadata
    for f in ['name', 'author', 'email', 'description', 'about', 'homepage', 'tracker']:
        if form.cleaned_data.get(f):
            setattr(plugin, f, form.cleaned_data.get(f))

    # Icon has a special treatment
    if form.cleaned_data.get('icon_file'):
        setattr(plugin, 'icon', form.cleaned_data.get('icon_file'))
    if form.cleaned_data.get('tags'):
        plugin.tags.set(*[t.strip().lower() for t in form.cleaned_data.get('tags').split(',')])
    plugin.save()


@login_required
def version_create(request, package_name):
    """
    The form will create versions according to permissions,
    plugin name and description are updated according to the info
    contained in the package metadata
    """
    plugin = get_object_or_404(Plugin, package_name=package_name)
    if not check_plugin_access(request.user, plugin):
        return render_to_response('plugins/version_permission_deny.html', { 'plugin' : plugin }, context_instance=RequestContext(request))

    version = PluginVersion(plugin = plugin, created_by = request.user)
    if request.method == 'POST':

        form = PluginVersionForm(request.POST, request.FILES, instance=version, is_trusted=request.user.has_perm('plugins.can_approve'))
        if form.is_valid():
            try:
                new_object = form.save()
                msg = _("The Plugin Version has been successfully created.")
                messages.success(request, msg, fail_silently=True)
                # The approved flag is also controlled in the form, but we
                # are checking it here in any case for additional security
                if not request.user.has_perm('plugins.can_approve'):
                    new_object.approved = False
                    new_object.save()
                    messages.warning(request, _('You do not have approval permissions, plugin version has been set unapproved.'), fail_silently=True)
                if form.cleaned_data.get('icon_file'):
                    form.cleaned_data['icon'] = form.cleaned_data.get('icon_file')
                _main_plugin_update(request, new_object.plugin, form)
                _check_optional_metadata(form, request)
                return HttpResponseRedirect(new_object.plugin.get_absolute_url())
            except (IntegrityError, ValidationError, DjangoUnicodeDecodeError), e:
                messages.error(request, e, fail_silently=True)
                connection.close()
            return HttpResponseRedirect(plugin.get_absolute_url())
    else:
        form = PluginVersionForm(is_trusted=request.user.has_perm('plugins.can_approve'))

    return render_to_response('plugins/version_form.html', {
        'form' : form,
        'plugin' : plugin,
        'form_title' : _('New version for plugin')
    }, context_instance=RequestContext(request))


@login_required
def version_update(request, package_name, version):
    """
    The form will update versions according to permissions
    """
    plugin =  get_object_or_404(Plugin, package_name=package_name)
    version = get_object_or_404(PluginVersion, plugin=plugin, version=version)
    if not check_plugin_access(request.user, plugin):
        return render_to_response('plugins/version_permission_deny.html', { 'plugin' : plugin }, context_instance=RequestContext(request))

    if request.method == 'POST':
        form = PluginVersionForm(request.POST, request.FILES, instance=version, is_trusted=request.user.has_perm('plugins.can_approve'))
        if form.is_valid():
            try:
                new_object = form.save()
                # update metadata for the main plugin object
                _main_plugin_update(request, new_object.plugin, form)
                msg = _("The Plugin Version has been successfully updated.")
                messages.success(request, msg, fail_silently=True)
            except (IntegrityError, ValidationError, DjangoUnicodeDecodeError), e:
                messages.error(request, e, fail_silently=True)
                connection.close()
            return HttpResponseRedirect(plugin.get_absolute_url())
    else:
        form = PluginVersionForm(instance=version, is_trusted=request.user.has_perm('plugins.can_approve'))

    return render_to_response('plugins/version_form.html', {
        'form' : form,
        'plugin' : plugin,
        'version' : version,
        'form_title' : _('Edit version for plugin')
    }, context_instance=RequestContext(request))



@login_required
def version_delete(request, package_name, version):
    plugin =  get_object_or_404(Plugin, package_name=package_name)
    version = get_object_or_404(PluginVersion, plugin=plugin, version=version)
    if not check_plugin_access(request.user, plugin):
        return render_to_response('plugins/version_permission_deny.html', {}, context_instance=RequestContext(request))
    if 'delete_confirm' in request.POST:
        version.delete()
        msg = _("The Plugin Version has been successfully deleted.")
        messages.success(request, msg, fail_silently=True)
        return HttpResponseRedirect(reverse('plugin_detail', args=(plugin.package_name,)))
    return render_to_response('plugins/version_delete_confirm.html', { 'plugin' : plugin, 'version' : version }, context_instance=RequestContext(request))



@login_required
@require_POST
def version_approve(request, package_name, version):
    """
    Approves the plugin version
    """
    plugin =  get_object_or_404(Plugin, package_name=package_name)
    version = get_object_or_404(PluginVersion, plugin=plugin, version=version)
    if not check_plugin_version_approval_rights(request.user, version.plugin):
        msg = _("You do not have approval rights for this plugin.")
        messages.error(request, msg, fail_silently=True)
        return HttpResponseRedirect(version.get_absolute_url())
    version.approved = True
    version.save()
    msg = unicode(_("The plugin version \"%s\" is now approved" % version))
    messages.success(request, msg, fail_silently=True)
    plugin_approve_notify(version.plugin, msg, request.user)
    try:
        redirect_to = request.META['HTTP_REFERER']
    except:
        redirect_to = version.get_absolute_url()
    return HttpResponseRedirect(redirect_to)


@login_required
@require_POST
def version_unapprove(request, package_name, version):
    """
    unapproves the plugin version
    """
    plugin =  get_object_or_404(Plugin, package_name=package_name)
    version = get_object_or_404(PluginVersion, plugin=plugin, version=version)
    if not check_plugin_version_approval_rights(request.user, version.plugin):
        msg = _("You do not have approval rights for this plugin.")
        messages.error(request, msg, fail_silently=True)
        return HttpResponseRedirect(version.get_absolute_url())
    version.approved = False
    version.save()
    msg = unicode(_("The plugin version \"%s\" is now unapproved" % version))
    messages.success(request, msg, fail_silently=True)
    plugin_approve_notify(version.plugin, msg, request.user)
    try:
        redirect_to = request.META['HTTP_REFERER']
    except:
        redirect_to = version.get_absolute_url()
    return HttpResponseRedirect(redirect_to)



@login_required
@require_POST
def version_manage(request, package_name, version):
    """
    Entry point for the user management functions
    """
    if request.POST.has_key('version_approve'):
        return version_approve(request, package_name, version)
    if request.POST.has_key('version_unapprove'):
        return version_unapprove(request, package_name, version)

    return HttpResponseRedirect(reverse('plugin_detail', args=[package_name]))


def version_download(request, package_name, version):
    """
    Update download counter(s)
    """
    plugin =  get_object_or_404(Plugin, package_name=package_name)
    version = get_object_or_404(PluginVersion, plugin=plugin, version=version)
    version.downloads = version.downloads + 1
    version.save()
    plugin = version.plugin
    plugin.downloads = plugin.downloads + 1
    plugin.save(keep_date=True)
    if not version.package.file.file.closed:
        version.package.file.file.close()
    zipfile = open(version.package.file.name, 'rb')
    file_content = zipfile.read()
    response = HttpResponse(file_content, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s-%s.zip' % (version.plugin.package_name, version.version)
    return response


def version_detail(request, package_name, version):
    """
    Show version details
    """
    plugin =  get_object_or_404(Plugin, package_name=package_name)
    version = get_object_or_404(PluginVersion, plugin=plugin, version=version)
    return render_to_response('plugins/version_detail.html', {'version' : version }, context_instance=RequestContext(request))


###############################################

# Misc functions

###############################################


def xml_plugins(request):
    """
    The XML file

    accepted parameters:

        * qgis: qgis version
        * stable_only: 0/1
        * package_name: Plugin.package_name

    """
    qg_version = vjust(request.GET.get('qgis', '1.8.0'), fillchar='0', level=2, force_zero=True)
    stable_only = request.GET.get('stable_only', '0')
    package_name = request.GET.get('package_name', None)

    filters = {}
    version_filters = {}
    object_list = []

    if qg_version:
        filters.update({'pluginversion__min_qg_version__lte' : qg_version})
        version_filters.update({'min_qg_version__lte' : qg_version})
        filters.update({'pluginversion__max_qg_version__gte' : qg_version})
        version_filters.update({'max_qg_version__gte' : qg_version})

    # Get all versions for the given plugin
    if package_name:
        filters.update({'package_name' : package_name})
        try:
            plugin = Plugin.approved_objects.get(**filters)
            plugin_version_filters = copy.copy(version_filters)
            plugin_version_filters.update({'plugin' : plugin})
            for plugin_version in PluginVersion.stable_objects.filter(**plugin_version_filters):
                object_list.append(plugin_version)
            if stable_only != '1':
                for plugin_version in PluginVersion.experimental_objects.filter(**plugin_version_filters):
                    object_list.append(plugin_version)
        except Plugin.DoesNotExist:
            pass
    else:
        for plugin in Plugin.approved_objects.filter(**filters):
            plugin_version_filters = copy.copy(version_filters)
            plugin_version_filters.update({'plugin' : plugin})
            try:
                object_list.append(PluginVersion.stable_objects.filter(**plugin_version_filters)[0])
            except IndexError:
                pass
            if stable_only != '1':
                try:
                    object_list.append(PluginVersion.experimental_objects.filter(**plugin_version_filters)[0])
                except IndexError:
                    pass

    return render_to_response('plugins/plugins.xml', {'object_list': object_list}, content_type='text/xml', context_instance=RequestContext(request))

