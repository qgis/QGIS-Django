import datetime

from django.db import models
from django.db.models import F, Q
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


STYLES_STORAGE_PATH = getattr(settings,
                                 'PLUGINS_STORAGE_PATH', 'styles/%Y')


class StyleUnapprovedManager(models.Manager):
    """Custom Queryset Manager for Unapproved Style"""
    def get_queryset(self):
        return super().get_queryset().filter(
                approved=False, require_action=False
            ).order_by('upload_date').distinct()


class StyleApprovedManager(models.Manager):
    """Custom Queryset Manager for Unapproved Style"""
    def get_queryset(self):
        return super().get_queryset().filter(approved=True).order_by('upload_date')


class StyleRequireactionManager(models.Manager):
    """Custom Queryset Manager for reviewed style requires an action"""
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(approved=False, require_action=True)\
            .order_by('upload_date').distinct()


class StyleType(models.Model):
    """
    Style Type model
    """

    # symbol, name and desc
    # symbol_type e.g. "line"
    # name e.g. "Line"
    symbol_type = models.CharField(
        _('Symbol type'),
        help_text=_('This will be used to identify the type of a style. '
                    'The value will be extracted automatically from '
                    'the uploaded QGIS style XML file.'),
        max_length=256,
        unique=True)
    name = models.CharField(
        _('Name'),
        help_text=_('Default to the title case string of symbol_type. '
                    'e.g. line would become Line.'),
        max_length=256,
        unique=True)
    description = models.TextField(
        _('Description'),
        help_text=_('A short description of this style type.'),
        max_length=1000,
        blank=True,
        null=True)

    # icon image
    icon = models.ImageField(
        _('Icon'),
        help_text=_('Please ensure the icon file is 500x500 px '
                    'and in PNG format.'),
        upload_to=STYLES_STORAGE_PATH,
        blank=True,
        null=True)

    # Ordering for StyleType instance
    order = models.IntegerField(
        _('Order'),
        help_text=_('Order value for custom ordering.'),
        default=0)

    class Meta:
        ordering = ('order',)

    def __unicode__(self):
        return "%s" % (self.name)

    def __str__(self):
        return self.__unicode__()


class Style(models.Model):
    """
    Style Model.

    A style is an XML document exported from the QGIS Style manager.
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
        related_name='styles_created_by',
        on_delete=models.CASCADE)

    # style type
    style_type = models.ForeignKey(StyleType,
        verbose_name=_('Type'),
        help_text=_('The type of this style, this will automatically be read '
                    'from the XML file.'),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        db_index=True)

    # name and desc
    name = models.CharField(_('Name'),
        help_text=_('A unique name for this style. This will be initially '
                    'automatically taken from the uploaded XML file, but may '
                    'need manual revision if the name is not unique.'),
        max_length=256,
        unique=True)
    description = models.TextField(
        _('Description'),
        help_text=_('A description of this style.'),
        max_length=5000
    )

    # thumbnail
    thumbnail_image = models.ImageField(
        _('Thumbnail'),
        help_text=_('Please upload an image that represents this style. '
                    'The image should be square when uploaded.'),
        blank=True,
        null=True,
        upload_to=STYLES_STORAGE_PATH)

    # file
    xml_file = models.FileField(
        _('Style file'),
        help_text=_('A QGIS style file in XML format.'),
        upload_to=STYLES_STORAGE_PATH,
        validators=[FileExtensionValidator(allowed_extensions=['xml'])],
        null=False)

    # counter
    download_count = models.IntegerField(
        _('Downloads'),
        help_text=_('The number of times this style has been downloaded. '
                    'This is updated automatically.'),
        default=0,
        editable=False)

    # approval
    approved = models.BooleanField(
        _('Approved'),
        default=False,
        help_text=_('Set to True if you wish to approve this style.'),
        db_index=True)

    # require_action
    require_action = models.BooleanField(
        _('Requires Action'),
        default=False,
        help_text=_('Set to True if you require creator to update its style.'),
        db_index=True)

    # Manager
    objects = models.Manager()
    approved_objects = StyleApprovedManager()
    unapproved_objects = StyleUnapprovedManager()
    requireaction_objects = StyleRequireactionManager()

    @property
    def get_creator_name(self):
        if not self.creator.first_name and not self.creator.last_name:
            return self.creator.username
        return f"{self.creator.first_name} {self.creator.last_name}"

    def increase_download_counter(self):
        self.download_count += 1

    def get_absolute_url(self):
        return reverse('style_detail', args=(self.id,))

    def save(self, *args, **kwargs):
        """Update modified_date"""

        self.modified_date = datetime.datetime.now()
        super().save(*args, **kwargs)

    def __unicode__(self):
        return "%s" % (self.name)

    def __str__(self):
        return self.__unicode__()


class StyleReview(models.Model):
    # date
    review_date = models.DateTimeField(
        _('Reviewed on'),
        help_text=_('The review date. Automatically added on style review.'),
        auto_now_add=True,
        editable=False)

    # creator
    reviewer = models.ForeignKey(
        User,
        verbose_name=_('Reviewed by'),
        help_text=_('The user who reviewed this style.'),
        related_name='styles_reviewed_by',
        on_delete=models.CASCADE)

    # style
    style = models.ForeignKey(Style,
        verbose_name=_('Style'),
        help_text=_('The type of this style, this will automatically be read '
                    'from the XML file.'),
        blank=True,
        null=True,
        on_delete=models.CASCADE)

    # comment
    comment = models.TextField(
        _('Comment'),
        help_text=_('A review comment. Please write your review.'),
        max_length=1000,
        blank=True,
        null=True,)

    class Meta:
        ordering = ['review_date',]


    def __str__(self):
        return self.comment
