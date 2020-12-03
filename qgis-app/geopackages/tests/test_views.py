import os
import tempfile

from django.conf import settings
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from django.contrib.auth.models import User, Group
from geopackages.models import Geopackage, GeopackageReview

from geopackages.views import geopackage_notify, geopackage_update_notify

GPKG_DIR = os.path.join(os.path.dirname(__file__), "gpkgfiles")


class TestEmailNotification(TestCase):

    def setUp(self):
        self.thumbnail = os.path.join(GPKG_DIR, "thumbnail.png")
        self.gpkg_file = os.path.join(GPKG_DIR, "spiky-polygons.gpkg")
        self.creator = User.objects.create(
            username="creator", email="creator@email.com"
        )
        # set creator password to password
        self.creator.set_password("password")
        self.creator.save()
        self.staff = User.objects.create(
            username="staff", email="staff@email.com"
        )
        self.staff.set_password("password")
        self.staff.save()
        self.group = Group.objects.create(name="Style Managers")
        self.group.user_set.add(self.staff)

        self.gpkg = Geopackage.objects.create(
            creator=self.creator,
            name="spiky polygons",
            description="A GeoPackage for testing purpose",
            thumbnail_image=self.thumbnail,
            gpkg_file=SimpleUploadedFile(
                "spiky_polygons.gpkg", b"file content"
            )
        )

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
    def test_print_email_notification_in_console(self):
        gpkg = Geopackage.objects.first()
        geopackage_notify(gpkg)
        GeopackageReview.objects.create(
            reviewer=self.staff,
            geopackage=gpkg,
            comment="Rejected for testing purpose")
        gpkg.require_action=True
        gpkg.save()
        geopackage_update_notify(gpkg, self.creator, self.staff)
        GeopackageReview.objects.create(
            reviewer=self.staff,
            geopackage=gpkg,
            comment="Approved! This is for testing purpose")
        gpkg.approved = True
        gpkg.save()
        geopackage_update_notify(gpkg, self.creator, self.staff)



