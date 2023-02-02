from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("robocjk", "0012_auto_20211019_1307"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="repo_branch",
            field=models.CharField(default="master", max_length=50, verbose_name="Repo branch"),
        ),
    ]
