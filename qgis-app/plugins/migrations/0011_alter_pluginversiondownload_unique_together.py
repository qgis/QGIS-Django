# Generated by Django 4.2.13 on 2024-05-28 06:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plugins', '0010_merge_20240517_0729'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='pluginversiondownload',
            unique_together={('plugin_version', 'download_date', 'country_code', 'country_name')},
        ),
    ]
