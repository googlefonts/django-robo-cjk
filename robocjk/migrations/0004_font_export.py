from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("robocjk", "0003_project_export"),
    ]

    operations = [
        migrations.AddField(
            model_name="font",
            name="export_completed_at",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Export completed at"
            ),
        ),
        migrations.AddField(
            model_name="font",
            name="export_running",
            field=models.BooleanField(default=False, verbose_name="Export running"),
        ),
        migrations.AddField(
            model_name="font",
            name="export_started_at",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Export started at"
            ),
        ),
    ]
