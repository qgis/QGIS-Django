# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit_autosuggest.managers
import plugins.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Plugin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Created on')),
                ('modified_on', models.DateTimeField(verbose_name='Modified on', editable=False)),
                ('author', models.CharField(help_text="This is the plugin's original author, if different from the uploader, this field will appear in the XML and in the web GUI", max_length=256, verbose_name='Author')),
                ('email', models.EmailField(max_length=254, verbose_name='Author email')),
                ('homepage', models.URLField(null=True, verbose_name='Plugin homepage', blank=True)),
                ('repository', models.URLField(null=True, verbose_name='Code repository', blank=True)),
                ('tracker', models.URLField(null=True, verbose_name='Tracker', blank=True)),
                ('package_name', models.CharField(help_text="This is the plugin's internal name, equals to the main folder name", verbose_name='Package Name', unique=True, max_length=256, editable=False)),
                ('name', models.CharField(help_text='Must be unique', unique=True, max_length=256, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description')),
                ('about', models.TextField(null=True, verbose_name='About', blank=True)),
                ('icon', models.ImageField(upload_to=b'packages/%Y', null=True, verbose_name='Icon', blank=True)),
                ('downloads', models.IntegerField(default=0, verbose_name='Downloads', editable=False)),
                ('featured', models.BooleanField(default=False, db_index=True, verbose_name='Featured')),
                ('deprecated', models.BooleanField(default=False, db_index=True, verbose_name='Deprecated')),
                ('rating_votes', models.PositiveIntegerField(default=0, editable=False, blank=True)),
                ('rating_score', models.IntegerField(default=0, editable=False, blank=True)),
                ('created_by', models.ForeignKey(related_name='plugins_created_by', verbose_name='Created by', to=settings.AUTH_USER_MODEL)),
                ('owners', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
                ('tags', taggit_autosuggest.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'ordering': ('name',),
                'permissions': (('can_approve', 'Can approve plugins versions'),),
            },
        ),
        migrations.CreateModel(
            name='PluginVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Created on')),
                ('downloads', models.IntegerField(default=0, verbose_name='Downloads', editable=False)),
                ('min_qg_version', plugins.models.QGVersionZeroForcedField(max_length=32, verbose_name='Minimum QGIS version', db_index=True)),
                ('max_qg_version', plugins.models.QGVersionZeroForcedField(db_index=True, max_length=32, null=True, verbose_name='Maximum QGIS version', blank=True)),
                ('version', plugins.models.VersionField(max_length=32, verbose_name='Version', db_index=True)),
                ('changelog', models.TextField(null=True, verbose_name='Changelog', blank=True)),
                ('package', models.FileField(upload_to=b'packages/%Y', verbose_name='Plugin package')),
                ('experimental', models.BooleanField(default=False, help_text="Check this box if this version is experimental, leave unchecked if it's stable. Please note that this field might be overridden by metadata (if present).", db_index=True, verbose_name='Experimental flag')),
                ('approved', models.BooleanField(default=True, help_text='Set to false if you wish to unapprove the plugin version.', db_index=True, verbose_name='Approved')),
                ('created_by', models.ForeignKey(verbose_name='Created by', to=settings.AUTH_USER_MODEL)),
                ('plugin', models.ForeignKey(to='plugins.Plugin')),
            ],
            options={
                'ordering': ('plugin', '-version', 'experimental'),
            },
        ),
        migrations.AlterUniqueTogether(
            name='pluginversion',
            unique_together=set([('plugin', 'version')]),
        ),
    ]
