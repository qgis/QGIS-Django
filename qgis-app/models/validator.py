import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

MODEL_MAX_SIZE = getattr(settings, "MODEL_MAX_SIZE", 1000000)  # 1MB


def model_validator(model_file) -> bool:
    """GeoPackage File Validation"""

    try:
        if model_file.getbuffer().nbytes > MODEL_MAX_SIZE:
            raise ValidationError(
                _("File is too big. Max size is %s Megabytes")
                % (MODEL_MAX_SIZE / 1000000)
            )
    except AttributeError:
        try:
            model_file.seek(0, os.SEEK_END)
            print(model_file.seek(0, os.SEEK_END))
            if model_file.seek(0, os.SEEK_END) > MODEL_MAX_SIZE:
                raise ValidationError(
                    _("File is too big. Max size is %s Megabytes")
                    % (MODEL_MAX_SIZE / 1000000)
                )
        except AttributeError:
            try:
                if model_file.size > MODEL_MAX_SIZE:
                    raise ValidationError(
                        _("File is too big. Max size is %s Megabytes")
                        % (MODEL_MAX_SIZE / 1000000)
                    )
            except AttributeError:
                try:
                    if model_file.len > MODEL_MAX_SIZE:
                        raise ValidationError(
                            _("File is too big. Max size is %s Megabytes")
                            % (MODEL_MAX_SIZE / 1000000)
                        )
                except Exception:
                    raise ValidationError(_("Can not read this file."))
    return True
