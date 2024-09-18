from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken, api_settings
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from api.models import UserOutstandingToken
from django.contrib.auth.models import User
from django.test import TestCase


class UserTokenDetailViewTests(TestCase):
    fixtures = ["fixtures/simplemenu.json"]
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.refresh = RefreshToken.for_user(self.user)
        self.outstanding_token = OutstandingToken.objects.get(jti=self.refresh['jti'])
        self.user_token = UserOutstandingToken.objects.create(
            user=self.user,
            token=self.outstanding_token,
            is_blacklisted=False,
            is_newly_created=True
        )
        self.url = reverse('user_token_detail', args=[self.user_token.pk])

    def test_user_token_detail_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

    def test_user_token_detail_view_invalid_token(self):
        self.user_token.is_blacklisted = True
        self.user_token.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)


class TestUserTokenListView(TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        super(TestUserTokenListView, self).setUp()
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="password"
        )
        self.client.login(username="testuser", password="password")
        refresh = RefreshToken.for_user(self.user)
        jti = refresh[api_settings.JTI_CLAIM]
        outstanding_token = OutstandingToken.objects.get(jti=jti)
        UserOutstandingToken.objects.create(
            user=self.user,
            token=outstanding_token,
            is_blacklisted=False,
            is_newly_created=True
        )

    def test_user_token_list_view(self):
        url = reverse("user_token_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Description")
        self.assertTemplateUsed(response, "user_token_list.html")

    def test_user_token_list_view_no_tokens(self):
        UserOutstandingToken.objects.all().delete()
        url = reverse("user_token_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This list is empty!")
        self.assertTemplateUsed(response, "user_token_list.html")


class TestUserTokenCreate(TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        super(TestUserTokenCreate, self).setUp()
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="password"
        )
        self.client.login(username="testuser", password="password")

    def test_user_token_create(self):
        url = reverse("user_token_create")
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_token_detail.html")
        self.assertContains(response, "access_token")

    def test_user_token_create_redirect(self):
        url = reverse("user_token_create")
        response = self.client.post(url)
        self.assertRedirects(response, reverse("user_token_detail", args=[2]))


class TestUserTokenUpdate(TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        super(TestUserTokenUpdate, self).setUp()
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="password"
        )
        self.client.login(username="testuser", password="password")
        refresh = RefreshToken.for_user(self.user)
        jti = refresh[api_settings.JTI_CLAIM]
        self.outstanding_token = OutstandingToken.objects.get(jti=jti)
        self.user_token = UserOutstandingToken.objects.create(
            user=self.user,
            token=self.outstanding_token,
            is_blacklisted=False,
            is_newly_created=True,
        )
        self.url = reverse("user_token_update", args=[self.user_token.pk])

    def test_user_token_update_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_token_form.html")

    def test_user_token_update_post_valid(self):
        data = {"description": "Updated description"}
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse("user_token_list"))
        self.user_token.refresh_from_db()
        self.assertEqual(self.user_token.description, "Updated description")


class TestUserTokenDelete(TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        super(TestUserTokenDelete, self).setUp()
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="password"
        )
        self.client.login(username="testuser", password="password")
        refresh = RefreshToken.for_user(self.user)
        jti = refresh[api_settings.JTI_CLAIM]
        self.outstanding_token = OutstandingToken.objects.get(jti=jti)
        self.user_token = UserOutstandingToken.objects.create(
            user=self.user,
            token=self.outstanding_token,
            is_blacklisted=False,
            is_newly_created=True
        )

    def test_user_token_delete_view(self):
        url = reverse("user_token_delete", args=[self.user_token.pk])
        response = self.client.post(url, {"delete_confirm": True}, follow=True)
        self.assertRedirects(response, reverse("user_token_list"))
        self.user_token.refresh_from_db()
        self.assertTrue(self.user_token.is_blacklisted)
        self.outstanding_token.refresh_from_db()
        self.assertTrue(self.outstanding_token.blacklistedtoken)
        self.assertContains(response, "The token has been successfully deleted.")