from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("extra_settings", "0008_auto_20221024_0717"),
        ("robocjk", "0016_auto_20221122_1046"),
    ]

    operations = [
        migrations.CreateModel(
            name="Setting",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("extra_settings.setting",),
        ),
    ]
