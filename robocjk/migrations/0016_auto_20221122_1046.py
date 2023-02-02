from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("robocjk", "0015_characterglyph_atomicelement_layers_updated_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="atomicelement",
            name="deleted",
            field=models.BooleanField(default=False, verbose_name="Deleted"),
        ),
        migrations.AddField(
            model_name="atomicelementlayer",
            name="deleted",
            field=models.BooleanField(default=False, verbose_name="Deleted"),
        ),
        migrations.AddField(
            model_name="characterglyph",
            name="deleted",
            field=models.BooleanField(default=False, verbose_name="Deleted"),
        ),
        migrations.AddField(
            model_name="characterglyphlayer",
            name="deleted",
            field=models.BooleanField(default=False, verbose_name="Deleted"),
        ),
        migrations.AddField(
            model_name="deepcomponent",
            name="deleted",
            field=models.BooleanField(default=False, verbose_name="Deleted"),
        ),
    ]
