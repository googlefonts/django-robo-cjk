from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("robocjk", "0010_auto_20211011_1821"),
    ]

    operations = [
        migrations.AddField(
            model_name="atomicelement",
            name="status_downgraded",
            field=models.BooleanField(default=False, verbose_name="Status downgraded"),
        ),
        migrations.AddField(
            model_name="atomicelement",
            name="status_downgraded_at",
            field=models.DateTimeField(
                blank=True, default=None, null=True, verbose_name="Status downgraded at"
            ),
        ),
        migrations.AddField(
            model_name="characterglyph",
            name="status_downgraded",
            field=models.BooleanField(default=False, verbose_name="Status downgraded"),
        ),
        migrations.AddField(
            model_name="characterglyph",
            name="status_downgraded_at",
            field=models.DateTimeField(
                blank=True, default=None, null=True, verbose_name="Status downgraded at"
            ),
        ),
        migrations.AddField(
            model_name="deepcomponent",
            name="status_downgraded",
            field=models.BooleanField(default=False, verbose_name="Status downgraded"),
        ),
        migrations.AddField(
            model_name="deepcomponent",
            name="status_downgraded_at",
            field=models.DateTimeField(
                blank=True, default=None, null=True, verbose_name="Status downgraded at"
            ),
        ),
    ]
