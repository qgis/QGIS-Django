"""
Base Model for sharing file feature
"""
import datetime
import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class UnapprovedManager(models.Manager):
    """Custom Queryset Manager for Unapproved Resource"""
    def get_queryset(self):
        return super().get_queryset().filter(
                approved=False, require_action=False
            ).order_by('upload_date').distinct()


class ApprovedManager(models.Manager):
    """Custom Queryset Manager for Unapproved Resource"""
    def get_queryset(self):
        return super().get_queryset().filter(approved=True) \
            .order_by('upload_date')


class RequireActionManager(models.Manager):
    """Custom Queryset Manager for reviewed Resource requires an action"""
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(approved=False, require_action=True)\
            .order_by('upload_date').distinct()


class Resource(models.Model):
    """
    Abstract base class of Resource

    Child class must have the FileField
    """

    # uuid
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    # date
    upload_date = models.DateTimeField(
        _('Uploaded on'),
        help_text=_('The upload date. Automatically added on file upload.'),
        auto_now_add=True,
        editable=False)
    modified_date = models.DateTimeField(
        _('Modified on'),
        help_text=_('The upload date. Automatically added on file upload.'),
        editable=False)

    # creator
    creator = models.ForeignKey(
        User,
        verbose_name=_('Created by'),
        help_text=_('The user who uploaded this resource.'),
        on_delete=models.CASCADE)

    # name and desc
    name = models.CharField(_('Name'),
                            help_text=_('A unique name for this resource'),
                            max_length=256,
                            blank=False,
                            null=False,
                            unique=True)
    description = models.TextField(
        _('Description'),
        help_text=_('A description of this resource.'),
        max_length=5000,
        blank=False,
        null=False
    )

    # counter
    download_count = models.IntegerField(
        _('Downloads'),
        help_text=_('The number of times this resource has been downloaded. '
                    'This is updated automatically.'),
        default=0,
        editable=False)

    # approval
    approved = models.BooleanField(
        _('Approved'),
        default=False,
        help_text=_('Set to True if you wish to approve this resource.'),
        db_index=True)

    # require_action
    require_action = models.BooleanField(
        _('Requires Action'),
        default=False,
        help_text=_('Set to True if you require creator to update the '
                    'resource.'),
        db_index=True)

    # Manager
    objects = models.Manager()
    approved_objects = ApprovedManager()
    unapproved_objects = UnapprovedManager()
    requireaction_objects = RequireActionManager()

    class Meta:
        abstract = True

    @property
    def get_creator_name(self):
        if not self.creator.first_name and not self.creator.last_name:
            return self.creator.username
        return "%s %s" % (self.creator.first_name, self.creator.last_name)

    def increase_download_counter(self):
        self.download_count += 1

    def save(self, *args, **kwargs):
        # update modified file
        self.modified_date = datetime.datetime.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return "%s" % (self.name)


class ResourceReview(models.Model):
    """
    A Review Model.
    """
    # date
    review_date = models.DateTimeField(
        _('Reviewed on'),
        help_text=_('The review date. Automatically added on review '
                    'resource.'),
        auto_now_add=True,
        editable=False)

    # reviewer
    reviewer = models.ForeignKey(
        User,
        verbose_name=_('Reviewed by'),
        help_text=_('The user who reviewed this %(app_label)s.'),
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_related')

    # comment
    comment = models.TextField(
        _('Comment'),
        help_text=_('A review comment. Please write your review.'),
        max_length=1000,
        blank=True,
        null=True,)

    class Meta:
        abstract = True
        ordering = ['review_date']

    def __str__(self):
        return self.comment
