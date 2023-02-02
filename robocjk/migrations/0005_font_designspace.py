from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("robocjk", "0004_font_export"),
    ]

    operations = [
        migrations.AddField(
            model_name="font",
            name="designspace",
            field=models.JSONField(blank=True, null=True, verbose_name="Designspace"),
        ),
    ]
