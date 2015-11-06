# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plugins', '0005_auto_20151106_1540'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plugin',
            name='external_deps',
        ),
    ]
