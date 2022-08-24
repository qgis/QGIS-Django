from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from plugins.models import Plugin, PluginVersion


class TestPluginSimpleTag(TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self) -> None:
        self.creator = User.objects.create(
            username="creator", email="creator@email.com"
        )
        # set creator password to password
        self.creator.set_password("password")
        self.creator.save()
        self.plugin_name = "plugin_name_test"
        self.plugin = Plugin.objects.create(
            created_by=self.creator,
            name=self.plugin_name,
            package_name=self.plugin_name,
        )
        self.version = PluginVersion.objects.create(
            plugin=self.plugin,
            created_by=self.creator,
            version="1.1.0",
            min_qg_version="0.0.1",
            max_qg_version="2.2.0",
        )

    def tearDown(self) -> None:
        self.plugin.delete()
        self.creator.delete()
        self.version.delete()

    def test_return_plugin_name(self):
        url = reverse(
            "plugin_detail", kwargs={"package_name": self.plugin.package_name}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            bytes(
                "{} — QGIS Python Plugins Repository".format(self.plugin.name), "utf-8"
            )
            in response.content
        )

    def test_return_plugin_name_in_version_view(self):
        url = reverse(
            "version_detail",
            kwargs={
                "package_name": self.plugin.package_name,
                "version": self.version.version,
            },
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            bytes(
                "{plugin} {version} — QGIS Python Plugins Repository".format(
                    plugin=self.plugin.name, version=self.version.version
                ),
                "utf-8",
            )
            in response.content
        )
