# Generated by Django 2.2.25 on 2023-11-07 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plugins', '0002_pluginversiondownload'),
    ]

    operations = [
        migrations.AddField(
            model_name='plugin',
            name='allow_update_name',
            field=models.BooleanField(default=False, help_text='Allow name in metadata.txt to update the plugin name', verbose_name='Allow update name'),
        ),
    ]
