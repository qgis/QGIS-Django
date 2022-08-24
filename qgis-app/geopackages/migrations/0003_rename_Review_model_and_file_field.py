# Custom migration, rename GeopackageReview to Review

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("geopackages", "0002_auto_20201215_2123"),
    ]

    operations = [
        migrations.RenameField(
            model_name="geopackage",
            old_name="gpkg_file",
            new_name="file",
        ),
        migrations.RenameField(
            model_name="geopackagereview",
            old_name="geopackage",
            new_name="resource",
        ),
        migrations.RenameModel(old_name="GeopackageReview", new_name="Review"),
    ]
