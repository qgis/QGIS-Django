import os
import tempfile

from base.views.processing_view import resource_notify, resource_update_notify
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from styles.models import Style, StyleType
from django.utils.text import slugify
from django.utils.encoding import escape_uri_path


STYLE_DIR = os.path.join(os.path.dirname(__file__), "stylefiles")


class TestPageUserAnonymous(TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def test_url(self):
        url = reverse("style_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All Styles")
        self.assertContains(response, "Style Type")
        self.assertContains(response, "No data.")

    def test_upload(self):
        url = reverse("style_create")
        response = self.client.get(url)
        self.assertRedirects(response, "/accounts/login/?next=/styles/add/")


class TestUploadStyle(TestCase):
    fixtures = ["fixtures/auth.json", "fixtures/simplemenu.json"]

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def setUp(self):
        self.thumbnail = os.path.join(STYLE_DIR, "thumbnail.png")
        self.creator = User.objects.get(pk=2)
        # set creator password to password
        self.creator.set_password("password")
        self.creator.email = "creator@email.com"
        self.creator.save()
        self.staff = User.objects.get(pk=3)
        self.staff.email = "staff@email.com"
        self.staff.save()
        self.group = Group.objects.create(name="Style Managers")
        self.group.user_set.add(self.staff)
        # user is logging in to upload page
        self.client.login(username="creator", password="password")
        url = reverse("style_create")
        self.response = self.client.get(url)

    def test_upload_page_with_login(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "base/upload_form.html")
        self.assertContains(self.response, "Style")

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_upload_xml_file(self):
        url = reverse("style_create")
        f = os.path.join(STYLE_DIR, "cattrail.xml")
        with open(f) as xml_file:
            self.client.post(
                url,
                {
                    "file": xml_file,
                    "thumbnail_image": self.thumbnail,
                    "description": "This style is for testing only purpose",
                    "tags": "xml,style,test"
                },
            )
        self.assertEqual(self.response.status_code, 200)

        # Should send email to style managers
        self.assertEqual(
            mail.outbox[0].recipients(),
            ['staff@email.com']
        )

        # Should use the new email
        self.assertEqual(
            mail.outbox[0].from_email,
            settings.EMAIL_HOST_USER
        )

        # Check the tags
        self.assertEqual(
            Style.objects.get(name='Cat Trail').tags.filter(
                name__in=['xml', 'style', 'test']).count(),
            3)

        # style should be in Waiting Review
        url = reverse("style_unapproved")
        self.response = self.client.get(url)
        self.assertContains(self.response, "1 record found.")
        self.assertContains(self.response, "Cat Trail")
        self.assertContains(self.response, "Line")
        self.assertContains(self.response, "Creator")
        # style should not be in Requiring Update
        url = reverse("style_require_action")
        self.response = self.client.get(url)
        self.assertContains(self.response, "No data.")


@override_settings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend")
class TestModeration(TestCase):
    fixtures = ["fixtures/auth.json", "fixtures/simplemenu.json"]

    @classmethod
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def setUpTestData(cls):
        cls.thumbnail = os.path.join(STYLE_DIR, "thumbnail.png")
        cls.creator = User.objects.get(pk=2)
        # set creator's password to password
        cls.creator.set_password("password")
        cls.creator.email = "creator@email.com"
        cls.creator.save()
        cls.staff = User.objects.get(pk=3)
        # set staff's password to password
        cls.staff.set_password("password")
        cls.staff.email = "staff@email.com"
        cls.staff.save()
        # create group
        cls.group = Group.objects.create(name="Style Managers")
        cls.group.user_set.add(cls.staff)
        # upload a style xml
        c = Client()
        c.login(username="creator", password="password")
        url = reverse("style_create")
        f = os.path.join(STYLE_DIR, "legend_patch.xml")
        with open(f) as xml_file:
            c.post(
                url,
                {
                    "file": xml_file,
                    "thumbnail_image": cls.thumbnail,
                    "description": "This style is for testing only purpose",
                },
            )
        c.logout()
        cls.uploaded_style = Style.objects.filter(name="Building 3").first()

    def setUp(self):
        self._original_media_root = settings.MEDIA_ROOT
        self._temp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self._temp_media

    def tearDown(self):
        settings.MEDIA_ROOT = self._original_media_root

    def test_user_anonymous_should_not_see_moderation_link(self):
        url = reverse("style_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All Styles")
        self.assertNotContains(response, "Waiting Review")
        self.assertNotContains(response, "Requiring Update")

    def test_user_anonymous_should_redirect_from_moderation(self):
        url = reverse("style_unapproved")
        response = self.client.get(url)
        self.assertRedirects(response, "/accounts/login/?next=/styles/unapproved/")
        url = reverse("style_require_action")
        response = self.client.get(url)
        self.assertRedirects(response, "/accounts/login/?next=/styles/require_action/")

    def test_creator_should_see_moderation_list(self):
        self.client.login(username="creator", password="password")
        url = reverse("style_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All Styles")
        self.assertContains(response, "Waiting Review")
        # go to waiting review page
        url = reverse("style_unapproved")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 record found.")
        self.assertContains(response, "Building 3")
        self.assertContains(response, "Legendpatchshape")
        # do detail review
        url = reverse("style_detail", kwargs={"pk": self.uploaded_style.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Building 3")
        self.assertContains(response, "in review")
        self.assertNotContains(response, '<textarea name="comment"')
        self.assertNotContains(
            response,
            '<input type="submit" ' 'class="btn btn-primary" ' 'value="Submit Review">',
            html=True,
        )
        # go to requiring update page
        url = reverse("style_require_action")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No data.")

    def test_another_user_should_not_see_moderation_list(self):
        newuser = User.objects.create(
            username="newuser", email="newuser@email.com", is_staff=False
        )
        newuser.set_password("password")
        newuser.save()
        # go to waiting review page
        self.client.login(username="newuser", password="password")
        url = reverse("style_unapproved")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No data.")
        self.client.logout()

    def test_staff_should_see_moderation_detail(self):
        self.client.login(username="staff", password="password")
        url = reverse("style_detail", kwargs={"pk": self.uploaded_style.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<textarea name="comment"')
        self.assertContains(
            response,
            '<input type="submit" ' 'class="btn btn-primary" ' 'value="Submit Review">',
            html=True,
        )
        self.client.logout()

    def test_staff_reject_and_submit_comment(self):
        self.client.login(username="staff", password="password")
        url = reverse("style_review", kwargs={"pk": self.uploaded_style.id})
        response = self.client.post(
            url,
            {
                "approval": "reject",
                "comment": "This should be in requiring update page.",
            },
        )
        url = reverse("style_detail", kwargs={"pk": self.uploaded_style.id})
        self.assertRedirects(response, url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This should be in requiring update page.")
        self.assertContains(response, "Reviewed by Staff now")
        self.client.logout()
        # creator should find the rejected styles in requiring update page
        self.client.login(username="creator", password="password")
        url = reverse("style_require_action")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Building 3")

    def test_staff_approve(self):
        self.client.login(username="staff", password="password")
        url = reverse("style_review", kwargs={"pk": self.uploaded_style.id})
        response = self.client.post(
            url, {"approval": "approve", "comment": "This should be in Approve page."}
        )
        url = reverse("style_detail", kwargs={"pk": self.uploaded_style.id})
        self.assertRedirects(response, url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "This should be in Approve page.")
        self.assertContains(response, "Approved Date")
        self.client.logout()

    def test_anonymous_should_see_approved_styles(self):
        self.uploaded_style.approved = True
        self.uploaded_style.save()
        url = reverse("style_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All Styles")
        self.assertContains(response, "1 record found.")
        self.assertContains(response, "Creator")


class TestDownloadStyles(TestCase):
    fixtures = ["fixtures/auth.json", "fixtures/simplemenu.json"]

    def setUp(self):
        StyleType.objects.create(
            pk=1,
            symbol_type="line",
            name="Line",
            description="For testing purpose only.",
        )
        self.newstyle = Style.objects.create(
            pk=1,
            creator=User.objects.get(pk=2),
            style_type=StyleType.objects.get(pk=1),
            name="Blues",
            description="This file is saved in styles/tests/stylefiles folder",
            thumbnail_image="thumbnail.png",
            file="colorramp_blue.xml",
            download_count=0,
            approved=True,
        )

        self.newstyle_non_ascii = Style.objects.create(
            pk=2,
            creator=User.objects.get(pk=2),
            style_type=StyleType.objects.get(pk=1),
            name="三调符号库",
            description="This file is saved in styles/tests/stylefiles folder",
            thumbnail_image="thumbnail.png",
            file="三调符号库.xml",
            download_count=0,
            approved=True,
        )

    @override_settings(MEDIA_ROOT="styles/tests/stylefiles/")
    def test_anonymous_user_download(self):
        style = Style.objects.get(pk=1)
        self.assertEqual(style.download_count, 0)
        self.client.logout()
        url = reverse("style_download", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # download_count should be increased
        style = Style.objects.get(pk=1)
        self.assertEqual(style.download_count, 1)

    @override_settings(MEDIA_ROOT="styles/tests/stylefiles/")
    def test_non_ascii_name_download(self):
        style = Style.objects.get(pk=2)
        self.assertEqual(style.download_count, 0)
        self.client.logout()
        url = reverse("style_download", kwargs={"pk": 2})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Check if the Content-Disposition header is present in the response
        self.assertTrue('Content-Disposition' in response)

        style_name = escape_uri_path(slugify(style.name, allow_unicode=True))
        # Extract the filename from the Content-Disposition header
        content_disposition = response['Content-Disposition']
        _, params = content_disposition.split(';')
        downloaded_filename = params.split('=')[1].strip(' "').split("utf-8''")[1]

        # Check if the downloaded filename matches the original filename
        self.assertEqual(downloaded_filename, f"{style_name}.zip")


class TestStyleApprovalNotify(TestCase):
    fixtures = [
        "fixtures/auth.json",
        "fixtures/styles.json",
        "fixtures/simplemenu.json",
    ]

    def setUp(self):
        self.creator = User.objects.get(pk=2)
        self.creator.email = "creator@example.com"
        self.creator.save()
        self.staff = User.objects.get(pk=3)
        self.staff.email = "staff@example.com"
        self.staff.save()
        self.style_approved = Style.objects.get(pk=1)
        self.style_rejected = Style.objects.get(pk=2)
        self.style_new = Style.objects.get(pk=3)
        self.group = Group.objects.create(name="Style Managers")
        self.group.user_set.add(self.staff)

    def test_send_email_new_style_notification(self):
        resource_notify(self.style_new, resource_type="Style")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject, "A new Style has been created by creator."
        )
        self.assertIn("Style name is: New Cube Style", mail.outbox[0].body)
        self.assertIn("Style description is: This is a new cube", mail.outbox[0].body)

    def test_send_email_approved_style_notification(self):
        resource_update_notify(self.style_approved, self.creator, self.staff, "Style")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Style Cube approved notification.")
        self.assertIn("This style is approved for testing purpose", mail.outbox[0].body)

    def test_send_email_rejected_style_notification(self):
        resource_update_notify(self.style_rejected, self.creator, self.staff, "Style")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject, "Style Another Cube rejected notification."
        )
        self.assertIn("This style is rejected for testing purpose", mail.outbox[0].body)


@override_settings(MEDIA_ROOT="styles/tests/stylefiles/")
class TestSearch(TestCase):
    fixtures = [
        "fixtures/styles.json",
        "fixtures/auth.json",
        "fixtures/simplemenu.json",
    ]

    def setUp(self):
        self.staff = User.objects.get(pk=3)
        # set staff's password to password
        self.staff.set_password("password")
        self.staff.save()
        # change value of imageFile
        obj = Style.objects.get(pk=1)
        obj.thumbnail_image = "thumbnail.png"
        obj.save()
        obj = Style.objects.get(pk=2)
        obj.thumbnail_image = "thumbnail.png"
        obj.save()
        obj = Style.objects.get(pk=3)
        obj.thumbnail_image = "thumbnail.png"
        obj.save()

    def test_search_approved_styles_list(self):
        url = reverse("style_list")
        response = self.client.get(url)
        self.assertNotContains(response, 'Keyword: "None"')
        url = reverse("style_list") + "?q=cube"
        response = self.client.get(url)
        self.assertContains(
            response,
            '<p>Keyword: "<strong>cube</strong>" <br> '
            "Search result: 1 record found.</p>",
            html=True,
        )

    def test_search_waiting_review_styles_list(self):
        self.client.login(username="staff", password="password")
        url = reverse("style_unapproved")
        response = self.client.get(url)
        self.assertNotContains(response, 'Keyword: "None"')
        url = reverse("style_unapproved") + "?q=new"
        response = self.client.get(url)
        self.assertContains(
            response,
            '<p>Keyword: "<strong>new</strong>" <br> '
            "Search result: 1 record found.</p>",
            html=True,
        )

    def test_search_requiring_update_styles_list(self):
        self.client.login(username="staff", password="password")
        url = reverse("style_require_action")
        response = self.client.get(url)
        self.assertNotContains(response, 'Keyword: "None"')
        url = reverse("style_require_action") + "?q=another"
        response = self.client.get(url)
        self.assertContains(
            response,
            '<p>Keyword: "<strong>another</strong>" <br> '
            "Search result: 1 record found.</p>",
            html=True,
        )
        url = reverse("style_require_action") + "?q=new"
        response = self.client.get(url)
        self.assertContains(
            response,
            '<p>Keyword: "<strong>new</strong>" <br> '
            "Search result: no record found.</p>",
            html=True,
        )
