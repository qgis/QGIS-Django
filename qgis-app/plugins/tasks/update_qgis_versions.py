from celery import shared_task
from base.models.site_preferences import SitePreference
from plugins.utils import get_qgis_versions


@shared_task
def update_qgis_versions():
    """
    This background task fetches the QGIS versions from the GitHub QGIS releases
    and then updates the current QGIS version in the database.
    """
    site_preference = SitePreference.objects.first()
    if not site_preference:
        site_preference = SitePreference.objects.create()

    qgis_versions = get_qgis_versions()
    stored_qgis_versions = site_preference.qgis_versions.split(',')
    for qgis_version in qgis_versions:
        if qgis_version not in stored_qgis_versions:
            stored_qgis_versions.append(qgis_version)
    stored_qgis_versions = list(filter(None, stored_qgis_versions))
    stored_qgis_versions = [tuple(map(int, v.split('.'))) for v in stored_qgis_versions]
    stored_qgis_versions.sort(reverse=True)
    stored_qgis_versions = ['.'.join(map(str, v)) for v in stored_qgis_versions]

    site_preference.qgis_versions = ','.join(stored_qgis_versions)
    site_preference.save()
