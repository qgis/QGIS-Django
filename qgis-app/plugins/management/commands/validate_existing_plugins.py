"""A command to validate the existing zipfile Plugin Packages"""

import os
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from plugins.models import PluginVersion, PluginInvalid
from plugins.validator import validator


DOMAIN = Site.objects.get_current().domain


def send_email_notification(plugin, version, message, url_version, recipients):

    message = ('\r\nPlease update '
               'Plugin: %s '
               '- Version: %s\r\n'
               '\r\nIt failed to pass validation with message:'
               '\r\n%s\r\n'
               '\r\nLink: %s') % (plugin, version, message, url_version)
    send_mail(
        subject='Invalid Plugin Metadata Notification',
        message=_(message),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=True
    )


def get_recipients_email(plugin):
    receipt_email = []
    if plugin.created_by.email:
        receipt_email.append(plugin.created_by.email)
    if plugin.email:
        receipt_email.append(plugin.email)
    return receipt_email


def validate_zipfile_version(version):

    if not os.path.exists(version.package.url):
        return {
            'plugin': f'{version.plugin.name}',
            'created_by': f'{version.plugin.created_by}',
            'version': f'{version.version}',
            'version_id': version.id,
            'msg': [f'File does not exist. Please re-upload.'],
            'url': f'http://{DOMAIN}{version.get_absolute_url()}',
            'recipients_email': get_recipients_email(version.plugin)
        }

    with open(version.package.url, 'rb') as buf:
        package = InMemoryUploadedFile(
            buf,
            'tempfile',
            'filename.zip',
            'application/zip',
            1000000,  # ignore the filesize and assume it's 1MB
            'utf8')
        try:
            validator(package)
        except Exception as e:
            return {
                'plugin': f'{version.plugin.name}',
                'created_by': f'{version.plugin.created_by}',
                'version': f'{version.version}',
                'version_id': version.id,
                'msg': e.messages,
                'url': f'http://{DOMAIN}{version.get_absolute_url()}',
                'recipients_email': get_recipients_email(version.plugin)
            }
    return None


class Command(BaseCommand):

    help = ('Validate existing Plugins zipfile and send a notification email '
            'for invalid Plugin')

    def handle(self, *args, **options):
        self.stdout.write('Validating existing plugins...')
        # get the latest version
        versions = PluginVersion.approved_objects.\
            order_by('plugin_id', '-created_on').distinct('plugin_id').all()[:50]
        num_count = 0
        for version in versions:
            error_msg = validate_zipfile_version(version)
            if error_msg:
                send_email_notification(
                    plugin=error_msg['plugin'],
                    version=error_msg['version'],
                    message='\r\n'.join(error_msg['msg']),
                    url_version=error_msg['url'],
                    recipients=error_msg['recipients_email']
                )
                self.stdout.write(
                    _('Sent email to %s for Plugin %s - Version %s.') % (
                        error_msg['recipients_email'],
                        error_msg['plugin'],
                        error_msg['version']
                    )
                )
                num_count += 1
                plugin_version = PluginVersion.objects\
                    .select_related('plugin').get(id=error_msg['version_id'])
                PluginInvalid.objects.create(
                    plugin=plugin_version.plugin,
                    validated_version=plugin_version.version,
                    message=error_msg['msg']
                )
        self.stdout.write(
            _('Successfully sent email notification for %s invalid plugins')
            % (num_count)
        )
