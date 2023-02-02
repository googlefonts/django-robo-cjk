from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("robocjk", "0011_auto_20211013_1153"),
    ]

    operations = [
        migrations.AddField(
            model_name="font",
            name="last_full_export_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Last full export at"),
        ),
        migrations.AddField(
            model_name="project",
            name="last_full_export_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Last full export at"),
        ),
    ]
