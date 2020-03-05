# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from plugins.tasks.generate_plugins_xml import generate_plugins_xml


class Command(BaseCommand):

    help = 'Fetch and cached plugins xml'

    def handle(self, *args, **options):
        generate_plugins_xml.delay()
