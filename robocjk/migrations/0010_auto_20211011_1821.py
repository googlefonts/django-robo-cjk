from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("robocjk", "0009_auto_20211008_1148"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="atomicelement",
            options={
                "verbose_name": "Atomic Element",
                "verbose_name_plural": "Atomic Elements",
            },
        ),
        migrations.AlterModelOptions(
            name="atomicelementlayer",
            options={
                "verbose_name": "Atomic Element Layer",
                "verbose_name_plural": "Atomic Element Layers",
            },
        ),
        migrations.AlterModelOptions(
            name="characterglyph",
            options={
                "verbose_name": "Character Glyph",
                "verbose_name_plural": "Character Glyphs",
            },
        ),
        migrations.AlterModelOptions(
            name="characterglyphlayer",
            options={
                "verbose_name": "Character Glyph Layer",
                "verbose_name_plural": "Character Glyph Layers",
            },
        ),
        migrations.AlterModelOptions(
            name="deepcomponent",
            options={
                "verbose_name": "Deep Component",
                "verbose_name_plural": "Deep Components",
            },
        ),
        migrations.AddField(
            model_name="atomicelement",
            name="previous_status",
            field=models.CharField(
                choices=[
                    ("wip", "Wip"),
                    ("checking-1", "Checking 1"),
                    ("checking-2", "Checking 2"),
                    ("checking-3", "Checking 3"),
                    ("done", "Done"),
                ],
                db_index=True,
                default="wip",
                max_length=20,
                verbose_name="Previous status",
            ),
        ),
        migrations.AddField(
            model_name="atomicelement",
            name="status_changed_at",
            field=models.DateTimeField(
                blank=True, default=None, null=True, verbose_name="Status changed at"
            ),
        ),
        migrations.AddField(
            model_name="characterglyph",
            name="previous_status",
            field=models.CharField(
                choices=[
                    ("wip", "Wip"),
                    ("checking-1", "Checking 1"),
                    ("checking-2", "Checking 2"),
                    ("checking-3", "Checking 3"),
                    ("done", "Done"),
                ],
                db_index=True,
                default="wip",
                max_length=20,
                verbose_name="Previous status",
            ),
        ),
        migrations.AddField(
            model_name="characterglyph",
            name="status_changed_at",
            field=models.DateTimeField(
                blank=True, default=None, null=True, verbose_name="Status changed at"
            ),
        ),
        migrations.AddField(
            model_name="deepcomponent",
            name="previous_status",
            field=models.CharField(
                choices=[
                    ("wip", "Wip"),
                    ("checking-1", "Checking 1"),
                    ("checking-2", "Checking 2"),
                    ("checking-3", "Checking 3"),
                    ("done", "Done"),
                ],
                db_index=True,
                default="wip",
                max_length=20,
                verbose_name="Previous status",
            ),
        ),
        migrations.AddField(
            model_name="deepcomponent",
            name="status_changed_at",
            field=models.DateTimeField(
                blank=True, default=None, null=True, verbose_name="Status changed at"
            ),
        ),
    ]
