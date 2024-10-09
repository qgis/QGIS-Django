from base.models.processing_models import Resource
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from django.contrib.auth.models import User

class UserOutstandingToken(models.Model):
    """
    Hub outstanding token
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    token = models.ForeignKey(
        OutstandingToken,
        on_delete=models.CASCADE
    )
    is_blacklisted = models.BooleanField(default=False)
    is_newly_created = models.BooleanField(default=False)
    description = models.CharField(
        verbose_name=_("Description"),
        help_text=_("Describe this token so that it's easier to remember where you're using it."),
        max_length=512,
        blank=True,
        null=True,
    )
    last_used_on = models.DateTimeField(
        verbose_name=_("Last used on"),
        blank=True,
        null=True
    )