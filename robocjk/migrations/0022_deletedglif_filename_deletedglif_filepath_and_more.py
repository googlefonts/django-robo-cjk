from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("robocjk", "0021_deletedglif"),
    ]

    operations = [
        migrations.AddField(
            model_name="deletedglif",
            name="filename",
            field=models.CharField(blank=True, max_length=50, verbose_name="Filename"),
        ),
        migrations.AddField(
            model_name="deletedglif",
            name="filepath",
            field=models.CharField(blank=True, max_length=255, verbose_name="Filepath"),
        ),
        migrations.AddField(
            model_name="deletedglif",
            name="group_name",
            field=models.CharField(
                blank=True, db_index=True, max_length=50, verbose_name="Group Name"
            ),
        ),
        migrations.AddField(
            model_name="deletedglif",
            name="name",
            field=models.CharField(
                blank=True, db_index=True, max_length=50, verbose_name="Name"
            ),
        ),
        migrations.AlterField(
            model_name="deletedglif",
            name="glif_id",
            field=models.PositiveIntegerField(db_index=True, verbose_name="Glif ID"),
        ),
        migrations.AlterField(
            model_name="deletedglif",
            name="glif_type",
            field=models.CharField(
                choices=[
                    ("atomic_element", "Atomic Element"),
                    ("atomic_element_layer", "Atomic Element Layer"),
                    ("deep_component", "Deep Component"),
                    ("character_glyph", "Character Glyph"),
                    ("character_glyph_layer", "Character Glyph Layer"),
                ],
                db_index=True,
                max_length=50,
                verbose_name="Glif Type",
            ),
        ),
    ]
