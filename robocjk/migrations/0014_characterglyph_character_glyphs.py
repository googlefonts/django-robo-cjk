from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("robocjk", "0013_project_repo_branch"),
    ]

    operations = [
        migrations.AddField(
            model_name="characterglyph",
            name="character_glyphs",
            field=models.ManyToManyField(
                blank=True,
                related_name="used_by_character_glyphs",
                to="robocjk.CharacterGlyph",
                verbose_name="Character Glyphs",
            ),
        ),
    ]
