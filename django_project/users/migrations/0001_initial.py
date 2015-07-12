# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='QgisUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('geometry', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('name', models.TextField()),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('image', models.ImageField(null=True, upload_to=b'user-pics', blank=True)),
                ('home_url', models.URLField(null=True, blank=True)),
                ('added_date', models.DateTimeField(auto_now=True, verbose_name=b'DateAdded')),
                ('guid', models.CharField(unique=True, max_length=40)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'QGIS User',
                'verbose_name_plural': 'QGIS Users',
            },
        ),
    ]
