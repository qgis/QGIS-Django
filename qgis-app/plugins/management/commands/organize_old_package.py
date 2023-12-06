# myapp/management/commands/organize_packages.py
import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from plugins.models import PluginVersion

PLUGINS_STORAGE_PATH = getattr(settings, "PLUGINS_STORAGE_PATH", "packages")
class Command(BaseCommand):
    help = 'Organize packages created before 2014 into folders by year'

    def handle(self, *args, **options):
        packages_dir = os.path.join(settings.MEDIA_ROOT, PLUGINS_STORAGE_PATH)

        # Some of the packages created on 2014 also need to be organized
        versions = PluginVersion.objects.filter(created_on__lt='2014-12-31').exclude(package__icontains='2014/')
        self.stdout.write(self.style.NOTICE(f'{versions.count()} packages will be organized.'))

        for version in versions:
            year_folder = os.path.join(packages_dir, str(version.created_on.year))

            # Create the year folder if it doesn't exist
            os.makedirs(year_folder, exist_ok=True)

            # Move the package file to the year folder
            old_path = version.package.path
            if os.path.exists(old_path):
                new_path = os.path.join(year_folder, os.path.basename(old_path))
                if not os.path.exists(new_path):
                    shutil.move(old_path, year_folder)

                    # Update the model with the new package path
                    version.package.name = os.path.relpath(new_path, settings.MEDIA_ROOT)
                    version.save()
                else:
                    self.stdout.write(self.style.WARNING(f'Plugin version id {version.pk} ignored: {new_path} already exists.'))
            else:
                self.stdout.write(self.style.WARNING(f'Plugin version id {version.pk} ignored: {old_path} is not found.'))

        self.stdout.write(self.style.SUCCESS('Packages organized successfully'))
