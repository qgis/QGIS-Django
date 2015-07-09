# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plugins', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plugin',
            name='about',
            field=models.TextField(null=True, verbose_name='About'),
        ),
        migrations.AlterField(
            model_name='plugin',
            name='repository',
            field=models.URLField(null=True, verbose_name='Code repository'),
        ),
        migrations.AlterField(
            model_name='plugin',
            name='tracker',
            field=models.URLField(null=True, verbose_name='Tracker'),
        ),
    ]
