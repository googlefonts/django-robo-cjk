from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("robocjk", "0006_project_repo_url_validator"),
    ]

    operations = [
        migrations.AlterField(
            model_name="font",
            name="designspace",
            field=models.JSONField(blank=True, default=dict, null=True, verbose_name="Designspace"),
        ),
    ]
