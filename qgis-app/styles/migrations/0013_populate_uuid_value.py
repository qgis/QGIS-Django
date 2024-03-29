# Generated by Django 2.2.13 on 2021-02-10 19:47

import uuid

from django.db import migrations


def gen_uuid(apps, schema_editor):
    Style = apps.get_model("styles", "Style")
    for row in Style.objects.all():
        row.uuid = uuid.uuid4()
        row.save(update_fields=["uuid"])


class Migration(migrations.Migration):

    dependencies = [
        ("styles", "0012_add_uuid_field"),
    ]

    operations = [
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop)
    ]
