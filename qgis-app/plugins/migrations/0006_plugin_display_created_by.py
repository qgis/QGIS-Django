# Generated by Django 2.2.25 on 2023-11-29 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plugins', '0005_plugin_maintainer'),
    ]

    operations = [
        migrations.AddField(
            model_name='plugin',
            name='display_created_by',
            field=models.BooleanField(default=False, verbose_name='Display "Created by" in plugin details'),
        ),
    ]
