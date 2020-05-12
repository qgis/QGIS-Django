# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from plugins.tasks.generate_plugins_xml import generate_plugins_xml


class Command(BaseCommand):

    help = 'Fetch and cached plugins xml'

    def add_arguments(self, parser):
        parser.add_argument(
            '-s',
            '--site',
            dest='site',
            default='http://plugins.qgis.org',
            help='Site url to get the source of plugins'
        )

    def handle(self, *args, **options):
        site = options.get('site')
        generate_plugins_xml.delay(site=site)
