"""
TODO:
- pagination
- email notification
- list page and custom queryset manager
"""
import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


GEOPACKAGES_STORAGE_PATH = getattr(settings,
                                 'PLUGINS_STORAGE_PATH', 'geopackages/%Y')


class GeopackageUnapprovedManager(models.Manager):
    """Custom Queryset Manager for Unapproved GeoPackage"""
    def get_queryset(self):
        return super().get_queryset().filter(
                approved=False, require_action=False
            ).order_by('upload_date').distinct()


class GeopackageApprovedManager(models.Manager):
    """Custom Queryset Manager for Unapproved GeoPackage"""
    def get_queryset(self):
        return super().get_queryset().filter(approved=True) \
            .order_by('upload_date')


class GeopackageRequireactionManager(models.Manager):
    """Custom Queryset Manager for reviewed GeoPackage requires an action"""
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(approved=False, require_action=True)\
            .order_by('upload_date').distinct()


class Geopackage(models.Model):
    """
    GeoPackage Model.

    A GeoPackage should come with:
    - a proper screenshot
    - description explaining what project demonstrate
    - filesize < 1 mb
    """

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
        help_text=_('The user who uploaded this style.'),
        related_name='gpkg_created_by',
        on_delete=models.CASCADE)

    # name and desc
    name = models.CharField(_('Name'),
                            help_text=_('A non-unique name for this '
                                        'GeoPackage.'),
                            max_length=256,
                            blank=False,
                            null=False,
                            unique=True)
    description = models.TextField(
        _('Description'),
        help_text=_('A description of this GeoPackage.'),
        max_length=5000,
        blank=False,
        null=False
    )

    # thumbnail
    thumbnail_image = models.ImageField(
        _('Thumbnail'),
        help_text=_('Please upload an image that demonstrate this '
                    'GeoPackage.'),
        blank=False,
        null=False,
        upload_to=GEOPACKAGES_STORAGE_PATH)

    # file
    gpkg_file = models.FileField(
        _('GeoPackage file'),
        help_text=_('A GeoPackage file. The filesize must less than 1MB '),
        upload_to=GEOPACKAGES_STORAGE_PATH,
        validators=[FileExtensionValidator(allowed_extensions=['gpkg'])],
        null=False)

    # counter
    download_count = models.IntegerField(
        _('Downloads'),
        help_text=_('The number of times this GeoPackage has been downloaded. '
                    'This is updated automatically.'),
        default=0,
        editable=False)

    # approval
    approved = models.BooleanField(
        _('Approved'),
        default=False,
        help_text=_('Set to True if you wish to approve this GeoPackage.'),
        db_index=True)

    # require_action
    require_action = models.BooleanField(
        _('Requires Action'),
        default=False,
        help_text=_('Set to True if you require creator to update '
                    'its GeoPackage.'),
        db_index=True)

    # Manager
    objects = models.Manager()
    approved_objects = GeopackageApprovedManager()
    unapproved_objects = GeopackageUnapprovedManager()
    requireaction_objects = GeopackageRequireactionManager()

    @property
    def get_creator_name(self):
        if not self.creator.first_name and not self.creator.last_name:
            return self.creator.username
        return "%s %s" % (self.creator.first_name, self.creator.last_name)

    def increase_download_counter(self):
        self.download_count += 1

    def get_absolute_url(self):
        return reverse('geopackage_detail', args=(self.id,))

    def save(self, *args, **kwargs):
        """Update modified_date"""

        self.modified_date = datetime.datetime.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return "%s" % (self.name)


class GeopackageReview(models.Model):
    """
    A GeoPackage Review Model.
    """
    # date
    review_date = models.DateTimeField(
        _('Reviewed on'),
        help_text=_('The review date. Automatically added on GeoPackage '
                    'review.'),
        auto_now_add=True,
        editable=False)

    # reviewer
    reviewer = models.ForeignKey(
        User,
        verbose_name=_('Reviewed by'),
        help_text=_('The user who reviewed this GeoPackage.'),
        related_name='geopackage_reviewed_by',
        on_delete=models.CASCADE)

    # geopackage
    geopackage = models.ForeignKey(Geopackage,
        verbose_name=_('GeoPackage'),
        help_text=_('The reviewed GeoPackage'),
        blank=False,
        null=False,
        on_delete=models.CASCADE)

    # comment
    comment = models.TextField(
        _('Comment'),
        help_text=_('A review comment. Please write your review.'),
        max_length=1000,
        blank=True,
        null=True,)

    class Meta:
        ordering = ['review_date']

    def __str__(self):
        return self.comment
