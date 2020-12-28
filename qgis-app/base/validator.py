import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

RESOURCE_MAX_SIZE = getattr(settings, 'RESOURCE_MAX_SIZE', 1000000)  # 1MB


def filesize_validator(file) -> bool:
    try:
        if file.getbuffer().nbytes > RESOURCE_MAX_SIZE:
            raise ValidationError(
                _("File is too big. Max size is %s Megabytes") % (
                        RESOURCE_MAX_SIZE / 1000000))
    except AttributeError:
        try:
            file.seek(0, os.SEEK_END)
            if file.seek(0, os.SEEK_END) > RESOURCE_MAX_SIZE:
                raise ValidationError(
                    _("File is too big. Max size is %s Megabytes") % (
                            RESOURCE_MAX_SIZE / 1000000))
        except AttributeError:
            try:
                if file.size > RESOURCE_MAX_SIZE:
                    raise ValidationError(
                    _("File is too big. Max size is %s Megabytes") % (
                        RESOURCE_MAX_SIZE / 1000000))
            except AttributeError:
                try:
                    if file.len > RESOURCE_MAX_SIZE:
                        raise ValidationError(
                        _("File is too big. Max size is %s Megabytes") % (
                        RESOURCE_MAX_SIZE / 1000000))
                except Exception:
                    raise ValidationError(_("Can not read this file."))
    return True
