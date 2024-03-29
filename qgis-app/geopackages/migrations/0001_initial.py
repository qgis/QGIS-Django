# Generated by Django 2.2 on 2020-12-01 20:23

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Geopackage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "upload_date",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="The upload date. Automatically added on file upload.",
                        verbose_name="Uploaded on",
                    ),
                ),
                (
                    "modified_date",
                    models.DateTimeField(
                        editable=False,
                        help_text="The upload date. Automatically added on file upload.",
                        verbose_name="Modified on",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="A non-unique name for this GeoPackage.",
                        max_length=256,
                        unique=True,
                        verbose_name="Name",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="A description of this GeoPackage.",
                        max_length=5000,
                        verbose_name="Description",
                    ),
                ),
                (
                    "thumbnail_image",
                    models.ImageField(
                        help_text="Please upload an image that demonstrate this GeoPackage.",
                        upload_to="geopackages/%Y",
                        verbose_name="Thumbnail",
                    ),
                ),
                (
                    "gpkg_file",
                    models.FileField(
                        help_text="A GeoPackage file. The filesize must less than 1MB ",
                        upload_to="geopackages/%Y",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=["gpkg"]
                            )
                        ],
                        verbose_name="GeoPackage file",
                    ),
                ),
                (
                    "download_count",
                    models.IntegerField(
                        default=0,
                        editable=False,
                        help_text="The number of times this GeoPackage has been downloaded. This is updated automatically.",
                        verbose_name="Downloads",
                    ),
                ),
                (
                    "approved",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="Set to True if you wish to approve this GeoPackage.",
                        verbose_name="Approved",
                    ),
                ),
                (
                    "require_action",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="Set to True if you require creator to update its GeoPackage.",
                        verbose_name="Requires Action",
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        help_text="The user who uploaded this style.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="gpkg_created_by",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created by",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="GeopackageReview",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "review_date",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="The review date. Automatically added on GeoPackage review.",
                        verbose_name="Reviewed on",
                    ),
                ),
                (
                    "comment",
                    models.TextField(
                        blank=True,
                        help_text="A review comment. Please write your review.",
                        max_length=1000,
                        null=True,
                        verbose_name="Comment",
                    ),
                ),
                (
                    "geopackage",
                    models.ForeignKey(
                        help_text="The reviewed GeoPackage",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="geopackages.Geopackage",
                        verbose_name="GeoPackage",
                    ),
                ),
                (
                    "reviewer",
                    models.ForeignKey(
                        help_text="The user who reviewed this GeoPackage.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="geopackage_reviewed_by",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Reviewed by",
                    ),
                ),
            ],
            options={
                "ordering": ["review_date"],
            },
        ),
    ]
