from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("robocjk", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="designers",
            field=models.ManyToManyField(
                blank=True,
                related_name="projects",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Designers",
            ),
        ),
    ]
