# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plugins', '0002_auto_20150613_0911'),
    ]

    operations = [
        migrations.AddField(
            model_name='plugin',
            name='external_deps',
            field=models.TextField(help_text='PIP install string', null=True, verbose_name='External dependencies'),
        ),
        migrations.AddField(
            model_name='plugin',
            name='server',
            field=models.BooleanField(default=False, db_index=True, verbose_name='Server'),
        ),
    ]
