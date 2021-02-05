# Custom migaration, rename Review class, rename file field, add related_name

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('styles', '0009_auto_20210121_0227'),
    ]

    operations = [
        migrations.RenameField(
            model_name='style',
            old_name='xml_file',
            new_name='file',
        ),

        migrations.RenameField(
            model_name='stylereview',
            old_name='style',
            new_name='resource',
        ),

        migrations.RenameModel(
            old_name='StyleReview',
            new_name='Review'
        ),

        migrations.AlterField(
            model_name='review',
            name='reviewer',
            field=models.ForeignKey(help_text='The user who reviewed this Style.',
                                    on_delete=django.db.models.deletion.CASCADE,
                                    related_name='styles_review_related', to=settings.AUTH_USER_MODEL,
                                    verbose_name='Reviewed by'),
        ),

    ]
