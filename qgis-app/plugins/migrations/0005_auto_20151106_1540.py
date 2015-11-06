# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plugins', '0004_pluginversion_external_deps'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pluginversion',
            name='external_deps',
            field=models.CharField(help_text='PIP install string', max_length=512, null=True, verbose_name='External dependencies'),
        ),
    ]
