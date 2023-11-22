# Custom migration, rename ModelReview to Review

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("models", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="model",
            old_name="model_file",
            new_name="file",
        ),
        migrations.RenameField(
            model_name="modelreview",
            old_name="model",
            new_name="resource",
        ),
        migrations.RenameModel(old_name="ModelReview", new_name="Review"),
        migrations.AlterField(
            model_name="review",
            name="reviewer",
            field=models.ForeignKey(
                help_text="The user who reviewed this GeoPackage.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="models_review_related",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Reviewed by",
            ),
        ),
    ]
