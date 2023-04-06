import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("robocjk", "0020_alter_atomicelement_unicode_hex_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeletedGlif",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("glif_id", models.PositiveIntegerField(verbose_name="Glif ID")),
                (
                    "glif_type",
                    models.CharField(
                        choices=[
                            ("atomic_element", "Atomic Element"),
                            ("atomic_element_layer", "Atomic Element Layer"),
                            ("deep_component", "Deep Component"),
                            ("character_glyph", "Character Glyph"),
                            ("character_glyph_layer", "Character Glyph Layer"),
                        ],
                        max_length=50,
                        verbose_name="Glif Type",
                    ),
                ),
                ("deleted_at", models.DateTimeField(verbose_name="Deleted at")),
                (
                    "deleted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Deleted by",
                    ),
                ),
                (
                    "font",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="deleted_glifs",
                        to="robocjk.font",
                        verbose_name="Font",
                    ),
                ),
            ],
            options={
                "verbose_name": "Deleted Glif",
                "verbose_name_plural": "Deleted Glifs",
            },
        ),
    ]
