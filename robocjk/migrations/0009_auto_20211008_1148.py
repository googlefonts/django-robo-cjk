from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("robocjk", "0008_auto_20210621_1611"),
    ]

    operations = [
        migrations.AddField(
            model_name="font",
            name="export_enabled",
            field=models.BooleanField(default=True, verbose_name="Export enabled"),
        ),
        migrations.AddField(
            model_name="project",
            name="export_enabled",
            field=models.BooleanField(default=True, verbose_name="Export enabled"),
        ),
    ]
