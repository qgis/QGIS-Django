"""
XML-RPC webservices for the plugin web application
"""

from io import BytesIO
from xmlrpc.server import Fault

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

# Transaction
from django.db import IntegrityError, connection
from django.utils.translation import ugettext_lazy as _
from plugins.models import *
from plugins.validator import validator
from plugins.views import plugin_notify
from rpc4django import rpcmethod
from taggit.models import Tag


@rpcmethod(name="plugin.maintainers", signature=["string"], login_required=True)
def plugin_maintaners(**kwargs):
    """
    Returns a CSV list of plugin maintainers
    """
    request = kwargs.get("request")
    if not request.user.is_superuser:
        raise PermissionDenied()
    return "\n".join(
        [
            u.email
            for u in User.objects.filter(
                plugins_created_by__isnull=False, email__isnull=False
            )
            .exclude(email="")
            .order_by("email")
            .distinct()
        ]
    )


@rpcmethod(name="plugin.upload", signature=["array", "base64"], login_required=True)
def plugin_upload(package, **kwargs):
    """
    Creates a new plugin or updates an existing one
    Returns an array containing the ID (primary key) of the plugin and the ID of the version.
    """
    try:

        request = kwargs.get("request")
        package = BytesIO(package)
        package.len = package.getbuffer().nbytes
        try:
            cleaned_data = dict(validator(package))
        except ValidationError as e:
            msg = _(
                "File upload must be a valid QGIS Python plugin compressed archive."
            )
            raise Fault(1, "%s %s" % (msg, ",".join(e.messages)))

        plugin_data = {
            "name": cleaned_data["name"],
            "package_name": cleaned_data["package_name"],
            "description": cleaned_data["description"],
            "created_by": request.user,
            "icon": cleaned_data["icon_file"],
            "author": cleaned_data["author"],
            "email": cleaned_data["email"],
            "about": cleaned_data["about"],
        }

        # Gets existing plugin
        if Plugin.objects.filter(
            name__iexact=plugin_data['name']
        ).exclude(package_name__iexact=plugin_data['package_name']).count():
            raise Fault(1, 'Error: The package name for this plugin has changed.')
        try:
            plugin = Plugin.objects.get(package_name=plugin_data["package_name"])
            # Apply new values
            plugin.name = plugin_data["name"]
            plugin.description = plugin_data["description"]
            plugin.icon = plugin_data["icon"]
            is_new = False
        except Plugin.DoesNotExist:
            plugin = Plugin(**plugin_data)
            is_new = True

        # Optional Metadata:
        if cleaned_data.get("homepage"):
            plugin.homepage = cleaned_data.get("homepage")
        if cleaned_data.get("tracker"):
            plugin.tracker = cleaned_data.get("tracker")
        if cleaned_data.get("repository"):
            plugin.repository = cleaned_data.get("repository")
        if cleaned_data.get("deprecated"):
            plugin.deprecated = cleaned_data.get("deprecated")

        plugin.save()

        if is_new:
            plugin_notify(plugin)

        # Takes care of tags
        if cleaned_data.get("tags"):
            plugin.tags.set(
                *[t.strip().lower() for t in cleaned_data.get("tags").split(",")]
            )

        version_data = {
            "plugin": plugin,
            "min_qg_version": cleaned_data["qgisMinimumVersion"],
            "version": cleaned_data["version"],
            "created_by": request.user,
            "package": InMemoryUploadedFile(
                package,
                "package",
                "%s.zip" % plugin.package_name,
                "application/zip",
                package.len,
                "UTF-8",
            ),
            "approved": request.user.has_perm("plugins.can_approve") or plugin.approved,
        }

        # Optional version metadata
        if cleaned_data.get("experimental"):
            version_data["experimental"] = cleaned_data.get("experimental")
        if cleaned_data.get("changelog"):
            version_data["changelog"] = cleaned_data.get("changelog")
        if cleaned_data.get("qgisMaximumVersion"):
            version_data["max_qg_version"] = cleaned_data.get("qgisMaximumVersion")

        new_version = PluginVersion(**version_data)
        new_version.clean()
        new_version.save()
    except IntegrityError as e:
        # Avoids error: current transaction is aborted, commands ignored until
        # end of transaction block
        connection.close()
        raise Fault(1, e.message)
    except ValidationError as e:
        raise Fault(1, e.message)
    except Exception as e:
        raise Fault(1, "%s" % e)

    return (plugin.pk, new_version.pk)


@rpcmethod(name="plugin.tags", signature=["array"], login_required=False)
def plugin_tags(**kwargs):
    """
    Returns a list of current tags, in alphabetical order
    """
    return [t.name for t in Tag.objects.all().order_by("name")]


@rpcmethod(
    name="plugin.vote", signature=["array", "integer", "integer"], login_required=False
)
def plugin_vote(plugin_id, vote, **kwargs):
    """
    Vote a plugin, valid values are 1-5
    """
    try:
        request = kwargs.get("request")
    except:
        msg = _("Invalid request.")
        raise ValidationError(msg)
    try:
        plugin = Plugin.objects.get(pk=plugin_id)
    except Plugin.DoesNotExist:
        msg = _("Plugin with id %s does not exists.") % plugin_id
        raise ValidationError(msg)
    if not int(vote) in range(1, 6):
        msg = _("%s is not a valid vote (1-5).") % vote
        raise ValidationError(msg)
    cookies = request.COOKIES
    if request.user.is_anonymous:
        # Get the cookie
        cookie_name = "vote-%s.%s.%s" % (
            ContentType.objects.get(app_label="plugins", model="plugin").pk,
            plugin_id,
            plugin.rating.field.key[:6],
        )
        if not request.COOKIES.get(cookie_name, False):
            # Get the IP
            ip_address = request.META["REMOTE_ADDR"]
            # Check if a recent vote exists
            rating = (
                plugin.rating.get_ratings()
                .filter(
                    cookie__isnull=False,
                    ip_address=ip_address,
                    date_changed__gte=datetime.datetime.now()
                    - datetime.timedelta(days=10),
                )
                .order_by("-date_changed")
            )
            # Change vote if exists
            if len(rating):
                cookies = {cookie_name: rating[0].cookie}
    return [
        plugin.rating.add(
            score=int(vote),
            user=request.user,
            ip_address=request.META["REMOTE_ADDR"],
            cookies=cookies,
        )
    ]
