from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

GPKG_MAX_SIZE = getattr(settings, 'GPKG_MAX_SIZE', 1000000)  # 1MB


def gpkg_validator(gpkg_file) -> bool:
    """GeoPackage File Validation"""

    try:
        if gpkg_file.getbuffer().nbytes > GPKG_MAX_SIZE:
            raise ValidationError(
                _("File is too big. Max size is %s Megabytes") % (
                        GPKG_MAX_SIZE / 1000000))
    except AttributeError:
        if gpkg_file.size > GPKG_MAX_SIZE:
            raise ValidationError(
                _("File is too big. Max size is %s Megabytes") % (
                        GPKG_MAX_SIZE / 1000000))
    return True
