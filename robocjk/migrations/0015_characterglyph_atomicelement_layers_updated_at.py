from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("robocjk", "0014_characterglyph_character_glyphs"),
    ]

    operations = [
        migrations.AddField(
            model_name="atomicelement",
            name="layers_updated_at",
            field=models.DateTimeField(
                blank=True,
                default=None,
                editable=False,
                null=True,
                verbose_name="Layers updated at",
            ),
        ),
        migrations.AddField(
            model_name="characterglyph",
            name="layers_updated_at",
            field=models.DateTimeField(
                blank=True,
                default=None,
                editable=False,
                null=True,
                verbose_name="Layers updated at",
            ),
        ),
    ]
