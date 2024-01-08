import os
from shutil import rmtree
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Run collectstatic and delete folders from media that exist in static'

    def handle(self, *args, **options):
        confirm = input("Do you want to run 'collectstatic' first? (yes/no): ")
        if confirm.lower() == 'yes':
            # Run collectstatic command
            call_command('collectstatic', interactive=False)

        # Get the paths of static and media folders
        static_root = settings.STATIC_ROOT
        media_root = settings.MEDIA_ROOT

        # Iterate over each directory in the static folder
        for static_dir in os.listdir(static_root):
            static_path = os.path.join(static_root, static_dir)

            # Check if the path is a directory and exists in the media folder
            if os.path.isdir(static_path) and os.path.exists(os.path.join(media_root, static_dir)):
                confirm = input(f"Are you sure you want to delete '{static_dir}' from the media folder? (yes/no): ")

                if confirm.lower() == 'yes':
                    try:
                        # Delete the corresponding folder in the media folder
                        rmtree(os.path.join(media_root, static_dir))
                        self.stdout.write(self.style.SUCCESS(f'Deleted {static_dir} from media folder.'))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f'Error deleting {static_dir}: {str(e)}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Skipped deletion of {static_dir}.'))

        self.stdout.write(self.style.SUCCESS('The media folder has been cleaned.'))
