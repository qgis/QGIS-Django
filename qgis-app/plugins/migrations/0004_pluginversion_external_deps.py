# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plugins', '0003_auto_20151106_1346'),
    ]

    operations = [
        migrations.AddField(
            model_name='pluginversion',
            name='external_deps',
            field=models.TextField(help_text='PIP install string', null=True, verbose_name='External dependencies'),
        ),
    ]
