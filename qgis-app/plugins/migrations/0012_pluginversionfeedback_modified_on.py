# Generated by Django 4.2.13 on 2024-06-13 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plugins', '0011_alter_pluginversiondownload_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='pluginversionfeedback',
            name='modified_on',
            field=models.DateTimeField(blank=True, editable=False, null=True, verbose_name='Modified on'),
        ),
    ]
