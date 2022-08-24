import os

import requests
from celery import shared_task
from django.conf import settings
from preferences import preferences


@shared_task
def generate_plugins_xml(site=""):
    """
    Fetch the xml list of plugins from the plugin site.
    :param site: site domain where the plugins will be fetched, default to
                 http://plugins.qgis.org
    """
    if not site:
        if settings.DEFAULT_PLUGINS_SITE:
            site = settings.DEFAULT_PLUGINS_SITE
        else:
            site = "http://plugins.qgis.org"
    plugins_url = "{}/plugins/plugins_new.xml".format(site)

    versions = preferences.SitePreference.qgis_versions

    if versions:
        versions = versions.split(",")
    else:
        versions = [
            "1.8",
            "2.0",
            "2.2",
            "2.4",
            "2.6",
            "2.8",
            "2.10",
            "2.12",
            "2.14",
            "2.15",
            "2.16",
            "2.17",
            "2.18",
            "2.99",
            "3.0",
            "3.1",
            "3.2",
            "3.3",
            "3.4",
            "3.5",
            "3.6",
            "3.7",
            "3.8",
            "3.9",
            "3.10",
            "3.11",
            "3.12",
            "3.13",
            "3.14",
            "3.15",
            "3.16",
            "3.17",
            "3.18",
            "3.19",
            "3.20",
            "3.21",
            "3.22",
            "3.23",
            "3.24",
            "3.25",
        ]

    folder_path = os.path.join(settings.MEDIA_ROOT, "cached_xmls")

    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

    for version in versions:
        response = requests.get(
            "{url}?qgis={version}".format(url=plugins_url, version=version)
        )

        if response.status_code == 200:
            file_name = "plugins_{}.xml".format(version)
            with open(os.path.join(folder_path, file_name), "w+") as file:
                file.write(response.text)
