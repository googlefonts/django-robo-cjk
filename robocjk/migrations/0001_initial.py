import uuid

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AtomicElement",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                (
                    "editors_history",
                    models.TextField(blank=True, verbose_name="Editors History"),
                ),
                (
                    "is_locked",
                    models.BooleanField(
                        db_index=True, default=False, verbose_name="Is Locked"
                    ),
                ),
                (
                    "locked_at",
                    models.DateTimeField(
                        blank=True, default=None, null=True, verbose_name="Locked at"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("wip", "Wip"),
                            ("checking-1", "Checking 1"),
                            ("checking-2", "Checking 2"),
                            ("checking-3", "Checking 3"),
                            ("done", "Done"),
                        ],
                        db_index=True,
                        default="wip",
                        max_length=20,
                        verbose_name="Status",
                    ),
                ),
                (
                    "data",
                    models.TextField(help_text="(.glif xml data)", verbose_name="Data"),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="(autodetected from xml data)",
                        max_length=50,
                        verbose_name="Name",
                    ),
                ),
                (
                    "filename",
                    models.CharField(
                        blank=True,
                        help_text="(.glif xml output filename, autodetected from xml data)",
                        max_length=50,
                        verbose_name="Filename",
                    ),
                ),
                (
                    "unicode_hex",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        default="",
                        help_text="(unicode hex value, autodetected from xml data)",
                        max_length=10,
                        verbose_name="Unicode hex",
                    ),
                ),
                ("components", models.TextField(blank=True, verbose_name="Components")),
                (
                    "is_empty",
                    models.BooleanField(
                        db_index=True,
                        default=True,
                        help_text="(autodetected from xml data)",
                        verbose_name="Is Empty",
                    ),
                ),
                (
                    "has_variation_axis",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Variation Axis",
                    ),
                ),
                (
                    "has_outlines",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Outlines",
                    ),
                ),
                (
                    "has_components",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Components",
                    ),
                ),
                (
                    "has_unicode",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Unicode",
                    ),
                ),
                (
                    "editors",
                    models.ManyToManyField(
                        related_name="_atomicelement_editors_+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Editors",
                    ),
                ),
            ],
            options={
                "verbose_name": "Atomic Element",
                "verbose_name_plural": "Atomic Elements",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Font",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "hashid",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        editable=False,
                        max_length=50,
                        verbose_name="Hash ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, verbose_name="Name")),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        editable=False,
                        null=True,
                        unique=True,
                        verbose_name="Slug",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                (
                    "editors_history",
                    models.TextField(blank=True, verbose_name="Editors History"),
                ),
                (
                    "uid",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, verbose_name="Unique ID"
                    ),
                ),
                (
                    "available",
                    models.BooleanField(
                        db_index=True, default=True, verbose_name="Available"
                    ),
                ),
                (
                    "fontlib",
                    models.JSONField(
                        blank=True, default=dict, null=True, verbose_name="FontLib"
                    ),
                ),
                ("features", models.TextField(blank=True, verbose_name="Features")),
                (
                    "editors",
                    models.ManyToManyField(
                        related_name="_font_editors_+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Editors",
                    ),
                ),
            ],
            options={
                "verbose_name": "Font",
                "verbose_name_plural": "Fonts",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Proof",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                (
                    "editors_history",
                    models.TextField(blank=True, verbose_name="Editors History"),
                ),
                (
                    "filetype",
                    models.CharField(
                        choices=[("pdf", ".pdf"), ("mp4", ".mp4")],
                        max_length=10,
                        verbose_name="Filetype",
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        upload_to="proofs",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=("pdf", "mp4")
                            )
                        ],
                        verbose_name="File",
                    ),
                ),
                (
                    "editors",
                    models.ManyToManyField(
                        related_name="_proof_editors_+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Editors",
                    ),
                ),
                (
                    "font",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="proofs",
                        to="robocjk.font",
                        verbose_name="Font",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Updated by",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "Proof",
                "verbose_name_plural": "Proofs",
                "ordering": ["-updated_at"],
            },
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "hashid",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        editable=False,
                        max_length=50,
                        verbose_name="Hash ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, verbose_name="Name")),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        editable=False,
                        null=True,
                        unique=True,
                        verbose_name="Slug",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                (
                    "editors_history",
                    models.TextField(blank=True, verbose_name="Editors History"),
                ),
                (
                    "uid",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, verbose_name="Unique ID"
                    ),
                ),
                (
                    "repo_url",
                    models.CharField(
                        help_text="The .git repository SSH URL, eg. git@github.com:username/repository.git",
                        max_length=200,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                "git\\@github\\.com\\:([\\w\\-\\_]+){1}\\/([\\w\\-\\_]+){1}\\.git",
                                "Invalid repository URL - Expected .git repository SSH URL, eg. git@github.com:username/repository.git",
                            )
                        ],
                        verbose_name="Repo URL",
                    ),
                ),
                (
                    "editors",
                    models.ManyToManyField(
                        related_name="_project_editors_+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Editors",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Updated by",
                    ),
                ),
            ],
            options={
                "verbose_name": "Project",
                "verbose_name_plural": "Projects",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="GlyphsComposition",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                (
                    "editors_history",
                    models.TextField(blank=True, verbose_name="Editors History"),
                ),
                (
                    "data",
                    models.JSONField(
                        blank=True, default=dict, null=True, verbose_name="Data"
                    ),
                ),
                (
                    "editors",
                    models.ManyToManyField(
                        related_name="_glyphscomposition_editors_+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Editors",
                    ),
                ),
                (
                    "font",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="glyphs_composition",
                        to="robocjk.font",
                        verbose_name="Font",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Updated by",
                    ),
                ),
            ],
            options={
                "verbose_name": "Glyphs Composition",
                "verbose_name_plural": "Glyphs Composition",
            },
        ),
        migrations.CreateModel(
            name="FontImport",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                (
                    "editors_history",
                    models.TextField(blank=True, verbose_name="Editors History"),
                ),
                (
                    "file",
                    models.FileField(
                        help_text=".zip file containing .rcjk font project.",
                        upload_to="fonts/imports",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=("zip",)
                            )
                        ],
                        verbose_name="File",
                    ),
                ),
                ("logs", models.TextField(blank=True, verbose_name="Logs")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("waiting", "Waiting"),
                            ("loading", "Loading"),
                            ("completed", "Completed"),
                            ("error", "Error"),
                        ],
                        db_index=True,
                        default="waiting",
                        max_length=20,
                        verbose_name="Status",
                    ),
                ),
                (
                    "editors",
                    models.ManyToManyField(
                        related_name="_fontimport_editors_+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Editors",
                    ),
                ),
                (
                    "font",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="robocjk.font",
                        verbose_name="Font",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Updated by",
                    ),
                ),
            ],
            options={
                "verbose_name": "Font Import",
                "verbose_name_plural": "Fonts Imports",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddField(
            model_name="font",
            name="project",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="fonts",
                to="robocjk.project",
                verbose_name="Project",
            ),
        ),
        migrations.AddField(
            model_name="font",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Updated by",
            ),
        ),
        migrations.CreateModel(
            name="DeepComponent",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                (
                    "editors_history",
                    models.TextField(blank=True, verbose_name="Editors History"),
                ),
                (
                    "is_locked",
                    models.BooleanField(
                        db_index=True, default=False, verbose_name="Is Locked"
                    ),
                ),
                (
                    "locked_at",
                    models.DateTimeField(
                        blank=True, default=None, null=True, verbose_name="Locked at"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("wip", "Wip"),
                            ("checking-1", "Checking 1"),
                            ("checking-2", "Checking 2"),
                            ("checking-3", "Checking 3"),
                            ("done", "Done"),
                        ],
                        db_index=True,
                        default="wip",
                        max_length=20,
                        verbose_name="Status",
                    ),
                ),
                (
                    "data",
                    models.TextField(help_text="(.glif xml data)", verbose_name="Data"),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="(autodetected from xml data)",
                        max_length=50,
                        verbose_name="Name",
                    ),
                ),
                (
                    "filename",
                    models.CharField(
                        blank=True,
                        help_text="(.glif xml output filename, autodetected from xml data)",
                        max_length=50,
                        verbose_name="Filename",
                    ),
                ),
                (
                    "unicode_hex",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        default="",
                        help_text="(unicode hex value, autodetected from xml data)",
                        max_length=10,
                        verbose_name="Unicode hex",
                    ),
                ),
                ("components", models.TextField(blank=True, verbose_name="Components")),
                (
                    "is_empty",
                    models.BooleanField(
                        db_index=True,
                        default=True,
                        help_text="(autodetected from xml data)",
                        verbose_name="Is Empty",
                    ),
                ),
                (
                    "has_variation_axis",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Variation Axis",
                    ),
                ),
                (
                    "has_outlines",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Outlines",
                    ),
                ),
                (
                    "has_components",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Components",
                    ),
                ),
                (
                    "has_unicode",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Unicode",
                    ),
                ),
                (
                    "atomic_elements",
                    models.ManyToManyField(
                        blank=True,
                        related_name="deep_components",
                        to="robocjk.AtomicElement",
                        verbose_name="Atomic Elements",
                    ),
                ),
                (
                    "editors",
                    models.ManyToManyField(
                        related_name="_deepcomponent_editors_+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Editors",
                    ),
                ),
                (
                    "font",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="deep_components",
                        to="robocjk.font",
                        verbose_name="Font",
                    ),
                ),
                (
                    "locked_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Locked by",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Updated by",
                    ),
                ),
            ],
            options={
                "verbose_name": "Deep Component",
                "verbose_name_plural": "Deep Components",
                "ordering": ["name"],
                "unique_together": {("font", "name")},
            },
        ),
        migrations.CreateModel(
            name="CharacterGlyph",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                (
                    "editors_history",
                    models.TextField(blank=True, verbose_name="Editors History"),
                ),
                (
                    "is_locked",
                    models.BooleanField(
                        db_index=True, default=False, verbose_name="Is Locked"
                    ),
                ),
                (
                    "locked_at",
                    models.DateTimeField(
                        blank=True, default=None, null=True, verbose_name="Locked at"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("wip", "Wip"),
                            ("checking-1", "Checking 1"),
                            ("checking-2", "Checking 2"),
                            ("checking-3", "Checking 3"),
                            ("done", "Done"),
                        ],
                        db_index=True,
                        default="wip",
                        max_length=20,
                        verbose_name="Status",
                    ),
                ),
                (
                    "data",
                    models.TextField(help_text="(.glif xml data)", verbose_name="Data"),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="(autodetected from xml data)",
                        max_length=50,
                        verbose_name="Name",
                    ),
                ),
                (
                    "filename",
                    models.CharField(
                        blank=True,
                        help_text="(.glif xml output filename, autodetected from xml data)",
                        max_length=50,
                        verbose_name="Filename",
                    ),
                ),
                (
                    "unicode_hex",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        default="",
                        help_text="(unicode hex value, autodetected from xml data)",
                        max_length=10,
                        verbose_name="Unicode hex",
                    ),
                ),
                ("components", models.TextField(blank=True, verbose_name="Components")),
                (
                    "is_empty",
                    models.BooleanField(
                        db_index=True,
                        default=True,
                        help_text="(autodetected from xml data)",
                        verbose_name="Is Empty",
                    ),
                ),
                (
                    "has_variation_axis",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Variation Axis",
                    ),
                ),
                (
                    "has_outlines",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Outlines",
                    ),
                ),
                (
                    "has_components",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Components",
                    ),
                ),
                (
                    "has_unicode",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Unicode",
                    ),
                ),
                (
                    "deep_components",
                    models.ManyToManyField(
                        blank=True,
                        related_name="character_glyphs",
                        to="robocjk.DeepComponent",
                        verbose_name="Deep Components",
                    ),
                ),
                (
                    "editors",
                    models.ManyToManyField(
                        related_name="_characterglyph_editors_+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Editors",
                    ),
                ),
                (
                    "font",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="character_glyphs",
                        to="robocjk.font",
                        verbose_name="Font",
                    ),
                ),
                (
                    "locked_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Locked by",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Updated by",
                    ),
                ),
            ],
            options={
                "verbose_name": "Character Glyph",
                "verbose_name_plural": "Character Glyphs",
                "ordering": ["name"],
                "unique_together": {("font", "name")},
            },
        ),
        migrations.AddField(
            model_name="atomicelement",
            name="font",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="atomic_elements",
                to="robocjk.font",
                verbose_name="Font",
            ),
        ),
        migrations.AddField(
            model_name="atomicelement",
            name="locked_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Locked by",
            ),
        ),
        migrations.AddField(
            model_name="atomicelement",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Updated by",
            ),
        ),
        migrations.CreateModel(
            name="CharacterGlyphLayer",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                (
                    "editors_history",
                    models.TextField(blank=True, verbose_name="Editors History"),
                ),
                (
                    "data",
                    models.TextField(help_text="(.glif xml data)", verbose_name="Data"),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="(autodetected from xml data)",
                        max_length=50,
                        verbose_name="Name",
                    ),
                ),
                (
                    "filename",
                    models.CharField(
                        blank=True,
                        help_text="(.glif xml output filename, autodetected from xml data)",
                        max_length=50,
                        verbose_name="Filename",
                    ),
                ),
                (
                    "unicode_hex",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        default="",
                        help_text="(unicode hex value, autodetected from xml data)",
                        max_length=10,
                        verbose_name="Unicode hex",
                    ),
                ),
                ("components", models.TextField(blank=True, verbose_name="Components")),
                (
                    "is_empty",
                    models.BooleanField(
                        db_index=True,
                        default=True,
                        help_text="(autodetected from xml data)",
                        verbose_name="Is Empty",
                    ),
                ),
                (
                    "has_variation_axis",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Variation Axis",
                    ),
                ),
                (
                    "has_outlines",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Outlines",
                    ),
                ),
                (
                    "has_components",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Components",
                    ),
                ),
                (
                    "has_unicode",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Unicode",
                    ),
                ),
                (
                    "group_name",
                    models.CharField(
                        db_index=True, max_length=50, verbose_name="Group Name"
                    ),
                ),
                (
                    "editors",
                    models.ManyToManyField(
                        related_name="_characterglyphlayer_editors_+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Editors",
                    ),
                ),
                (
                    "glif",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="layers",
                        to="robocjk.characterglyph",
                        verbose_name="Glif",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Updated by",
                    ),
                ),
            ],
            options={
                "verbose_name": "Character Glyph Layer",
                "verbose_name_plural": "Character Glyph Layers",
                "ordering": ["group_name"],
                "unique_together": {("glif_id", "group_name", "name")},
            },
        ),
        migrations.CreateModel(
            name="AtomicElementLayer",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                (
                    "editors_history",
                    models.TextField(blank=True, verbose_name="Editors History"),
                ),
                (
                    "data",
                    models.TextField(help_text="(.glif xml data)", verbose_name="Data"),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="(autodetected from xml data)",
                        max_length=50,
                        verbose_name="Name",
                    ),
                ),
                (
                    "filename",
                    models.CharField(
                        blank=True,
                        help_text="(.glif xml output filename, autodetected from xml data)",
                        max_length=50,
                        verbose_name="Filename",
                    ),
                ),
                (
                    "unicode_hex",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        default="",
                        help_text="(unicode hex value, autodetected from xml data)",
                        max_length=10,
                        verbose_name="Unicode hex",
                    ),
                ),
                ("components", models.TextField(blank=True, verbose_name="Components")),
                (
                    "is_empty",
                    models.BooleanField(
                        db_index=True,
                        default=True,
                        help_text="(autodetected from xml data)",
                        verbose_name="Is Empty",
                    ),
                ),
                (
                    "has_variation_axis",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Variation Axis",
                    ),
                ),
                (
                    "has_outlines",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Outlines",
                    ),
                ),
                (
                    "has_components",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Components",
                    ),
                ),
                (
                    "has_unicode",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="(autodetected from xml data)",
                        verbose_name="Has Unicode",
                    ),
                ),
                (
                    "group_name",
                    models.CharField(
                        db_index=True, max_length=50, verbose_name="Group Name"
                    ),
                ),
                (
                    "editors",
                    models.ManyToManyField(
                        related_name="_atomicelementlayer_editors_+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Editors",
                    ),
                ),
                (
                    "glif",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="layers",
                        to="robocjk.atomicelement",
                        verbose_name="Glif",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Updated by",
                    ),
                ),
            ],
            options={
                "verbose_name": "Atomic Element Layer",
                "verbose_name_plural": "Atomic Element Layers",
                "ordering": ["group_name"],
                "unique_together": {("glif_id", "group_name")},
            },
        ),
        migrations.AlterUniqueTogether(
            name="atomicelement",
            unique_together={("font", "name")},
        ),
    ]
