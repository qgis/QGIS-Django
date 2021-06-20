# Generated by Django 2.2.18 on 2021-06-20 10:00

from django.db import migrations, models
import django.db.models.deletion
import plugins.models


class Migration(migrations.Migration):

    dependencies = [
        ('plugins', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PluginInvalid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('validated_version', plugins.models.VersionField(db_index=True, max_length=32, verbose_name='Version')),
                ('validated_at', models.DateTimeField(auto_now_add=True, verbose_name='Validated at')),
                ('plugin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plugins.Plugin')),
            ],
        ),
    ]
