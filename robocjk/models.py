import datetime as dt
import multiprocessing

# import os
import subprocess

import fsutil
from benedict import benedict
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Max
from django.utils.encoding import force_str
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from robocjk.abstract_models import (
    ExportModel,
    HashidModel,
    NameSlugModel,
    TimestampModel,
    UIDModel,
)
from robocjk.api.serializers import (
    serialize_atomic_element,
    serialize_atomic_element_layer,
    serialize_character_glyph,
    serialize_character_glyph_layer,
    serialize_deep_component,
    serialize_font,
    serialize_project,
)
from robocjk.core import GlifData
from robocjk.debug import logger
from robocjk.io.paths import (
    get_atomic_element_layer_path,
    get_atomic_element_path,
    get_atomic_elements_path,
    get_character_glyph_layer_path,
    get_character_glyph_path,
    get_character_glyphs_path,
    get_deep_component_path,
    get_deep_components_path,
    get_font_path,
    get_project_path,
    get_proof_path,
)
from robocjk.managers import (
    AtomicElementLayerManager,
    AtomicElementManager,
    CharacterGlyphLayerManager,
    CharacterGlyphManager,
    DeepComponentManager,
    FontManager,
    ProjectManager,
)
from robocjk.signals import connect_signals
from robocjk.utils import format_glif, unicodes_str_to_list
from robocjk.validators import GitSSHRepositoryURLValidator

# import time


def run_commands(*args):
    cmds = args
    cmd = " && ".join(cmds)
    logger.info(f"Run commands: \n{cmd}")

    # # Run commands using os.system
    # os.system(cmd)

    # # Run commands using Popen
    # cmd_process = subprocess.Popen(cmd, shell=True)
    # cmd_process.wait()

    # Run commands using check_output
    cmd_output = b""
    try:
        cmd_output = subprocess.check_output(cmd, shell=True)
        cmd_output_str = cmd_output.decode("UTF-8")
        logger.info(f"Command output: {cmd_output_str}")
    except subprocess.CalledProcessError as error:
        # print("error code", error.returncode, error.output)
        if error.returncode == 1:
            # Your branch is up to date with 'origin/master'.
            # nothing to commit, working tree clean
            pass
        else:
            if error.returncode == 128:
                logger.error(
                    "Command returned non-zero exit status 128, "
                    "check if git repo and branch are correct."
                )
            cmd_output = error.output
            cmd_output_str = cmd_output.decode("UTF-8")
            logger.exception(f"Command error: {cmd_output_str}")
            raise error


class Project(UIDModel, HashidModel, NameSlugModel, TimestampModel, ExportModel):
    """
    The Project model.
    """

    class Meta:
        app_label = "robocjk"
        ordering = ["name"]
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    repo_url = models.CharField(
        unique=True,
        max_length=200,
        validators=[GitSSHRepositoryURLValidator()],
        verbose_name=_("Repo URL"),
        help_text=_(
            "The .git repository SSH URL, eg. git@github.com:username/repository.git"
        ),
    )

    repo_branch = models.CharField(
        max_length=50,
        default="master",
        verbose_name=_("Repo branch"),
    )

    designers = models.ManyToManyField(
        get_user_model(),
        blank=True,
        related_name="projects",
        verbose_name=_("Designers"),
    )

    objects = ProjectManager()

    def num_designers(self):
        return self.designers.count()

    def num_fonts(self):
        return self.fonts.count()

    def path(self):
        return get_project_path(self)

    def save_by(self, user):
        super().save_by(user)
        self.designers.add(user)

    def save_to_file_system(self, full_export=False):
        logger.info(f'Saving project "{self.name}" to file system...')
        path = self.path()
        fsutil.make_dirs(path)
        repo_path = fsutil.join_path(path, ".git")
        repo_branch = self.repo_branch or "main"
        if not fsutil.exists(repo_path):
            # repository doesn't exist, initialize it
            logger.info(
                f"Repository for project '{self.name}' doesn't exist, initialize it."
            )
            run_commands(
                f"cd {path}",
                "git init",
                f'git config --local --add "user.name" "{settings.GIT_USER_NAME}"',
                f'git config --local --add "user.email" "{settings.GIT_USER_EMAIL}"',
                f"git remote add origin {self.repo_url}",
                f"git pull origin {repo_branch}",
                f"git push --set-upstream origin {repo_branch}",
            )
        else:
            # repository exist
            logger.info(
                f'Repository for project "{self.name}" already exist, update it.'
            )
            run_commands(
                f"cd {path}",
                "git reset --hard",
                f"git checkout {repo_branch}",
                f"git pull origin {repo_branch}",
                "git clean -df",
            )
        # save all project fonts to file.system
        fonts_qs = self.fonts.all()
        fonts_list = list(fonts_qs)
        # cleanup - remove .rcjk projects that don't belong anymore to a project font
        fonts_rcjk_pulled_dirs = set(fsutil.search_dirs(path, "*.rcjk"))
        fonts_rcjk_dirs = {font.path() for font in fonts_list}
        fonts_rcjk_deleted_dirs = list(fonts_rcjk_pulled_dirs - fonts_rcjk_dirs)
        logger.info(
            f"Deleting project '{self.name}' old fonts "
            f"from file system... \n{fonts_rcjk_deleted_dirs}"
        )
        fsutil.remove_dirs(*fonts_rcjk_deleted_dirs)
        # save all project fonts to the file system
        export_strategy_name = "full" if full_export else "incremental"
        font_names = [font.name for font in fonts_list]
        logger.info(
            f"Saving project '{self.name}' fonts ({export_strategy_name} export) "
            f"to file system... \n{font_names}"
        )

        for font in fonts_list:
            font_dirpath = fsutil.get_filename(font.path())
            font_commit_message = font.get_commit_message()
            font_export_success = font.export(full=full_export)
            if font_export_success:
                # add all changed files, commit and push to the git repository
                run_commands(
                    f"cd {path}",
                    f"git add ./{font_dirpath}",
                    f'git commit -m "{font_commit_message}"',
                    f"git push origin {repo_branch}",
                )
        run_commands(
            f"cd {path}",
            "git add --all",
            'git commit -m "{}"'.format("Updated project."),
            f"git push origin {repo_branch}",
        )

    def serialize(self, options=None):
        return serialize_project(self, options)

    def __str__(self):
        return force_str(f"{self.name}")


def save_glif_to_file_system(glif_data):
    """
    Worker function for saving glif files to file-system.
    """
    # logger.debug('Saving glif "{}" to file system: {}'.format(glif, glif.path()))
    filepath, content = glif_data
    # file_exists = fsutil.exists(filepath)
    # assert not file_exists
    fsutil.write_file(filepath, content)
    # file_exists = fsutil.exists(filepath)
    # assert file_exists
    # return file_exists
    return True


class Font(UIDModel, HashidModel, NameSlugModel, TimestampModel, ExportModel):
    """
    The Font model.
    """

    class Meta:
        app_label = "robocjk"
        ordering = ["name"]
        verbose_name = _("Font")
        verbose_name_plural = _("Fonts")

    project = models.ForeignKey(
        "robocjk.Project",
        on_delete=models.CASCADE,
        related_name="fonts",
        verbose_name=_("Project"),
    )

    available = models.BooleanField(
        db_index=True,
        default=True,
        verbose_name=_("Available"),
    )

    fontlib = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        verbose_name=_("FontLib"),
    )

    features = models.TextField(
        blank=True,
        verbose_name=_("Features"),
    )

    designspace = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        verbose_name=_("Designspace"),
    )

    objects = FontManager()

    @cached_property
    def full_name(self):
        return f"{self.project.name} / {self.name}"

    def get_commit_message(self, **options):
        """
        Get the commit message for the font combining the font name and
        the list of users that worked on it since the last project export).
        """
        users_qs = self.updated_by_users(**options)
        users_names = [user.get_full_name() for user in users_qs]
        users_str = ", ".join(users_names)
        # return 'Updated {}.'.format(self.name)
        message = f"Updated {self.name}"
        if users_str:
            return f"{message} by: {users_str}."
        return f"{message}."

    def num_character_glyphs(self):
        return self.character_glyphs.count()

    def num_character_glyphs_layers(self):
        return CharacterGlyphLayer.objects.filter(glif__font=self).count()

    def num_deep_components(self):
        return self.deep_components.count()

    def num_atomic_elements(self):
        return self.atomic_elements.count()

    def num_atomic_elements_layers(self):
        return AtomicElementLayer.objects.filter(glif__font=self).count()

    def path(self):
        return get_font_path(self)

    def save_to_file_system(self, full_export=False):  # noqa: C901
        font = self
        font_name = font.full_name
        if not font.available:
            logger.info(
                f"Skipped font '{font_name}' saving because "
                f"it is not available (maybe there is an import running)."
            )
            return
        logger.info(f"Saving font '{font_name}' to file system...")
        font_path = font.path()
        fsutil.make_dirs(font_path)
        # write fontLib.json file
        logger.info(f"Saving font '{font_name}' 'fontLib.json' to file system...")
        fontlib_path = fsutil.join_path(font_path, "fontLib.json")
        fontlib_str = benedict(font.fontlib, keypath_separator=None).dump()
        fsutil.write_file(fontlib_path, fontlib_str)
        # write features.fea file
        logger.info(f"Saving font '{font_name}' 'features.fea' to file system...")
        features_path = fsutil.join_path(font_path, "features.fea")
        fsutil.write_file(features_path, font.features)
        # write designspace.json file
        logger.info(f"Saving font '{font_name}' 'designspace.json' to file system...")
        designspace_path = fsutil.join_path(font_path, "designspace.json")
        designspace_str = benedict(font.designspace, keypath_separator=None).dump()
        fsutil.write_file(designspace_path, designspace_str)
        # write glyphsComposition.json file
        logger.info(
            f"Saving font '{font_name}' 'glyphsComposition.json' to file system..."
        )
        glyphs_composition_obj, _ = GlyphsComposition.objects.get_or_create(
            font_id=font.id
        )
        glyphs_composition_path = fsutil.join_path(font_path, "glyphsComposition.json")
        glyphs_composition_str = benedict(
            glyphs_composition_obj.serialize(), keypath_separator=None
        ).dump()
        fsutil.write_file(glyphs_composition_path, glyphs_composition_str)

        # delete existing character-glyphs, deep-components and atomic-elements directories
        logger.info(
            f"Deleting font '{font_name}' character-glyphs, "
            "deep-components and atomic-elements folders..."
        )

        character_glyphs_path = get_character_glyphs_path(font)
        deep_components_path = get_deep_components_path(font)
        atomic_elements_path = get_atomic_elements_path(font)

        # cleanup glifs dirs/files
        updated_after = None
        if full_export:
            # remove existing glifs dirs
            fsutil.remove_dirs(
                character_glyphs_path,
                deep_components_path,
                atomic_elements_path,
            )
        else:
            # set updated_after only if not running a full export
            if font.export_started_at and font.export_completed_at:
                updated_after = min(font.export_started_at, font.export_completed_at)
            # delete possible zombie files of glifs that have been deleted
            if updated_after:
                deleted_glifs_qs = DeletedGlif.objects.select_related(
                    "font",
                ).filter(deleted_at__gt=updated_after)
                for deleted_glif_obj in deleted_glifs_qs:
                    deleted_glif_filepath = deleted_glif_obj.filepath
                    if fsutil.is_file(deleted_glif_filepath):
                        fsutil.remove_file(deleted_glif_filepath)

        # create empty dirs to avoid errors in fonts that have not all entities
        fsutil.make_dirs(character_glyphs_path)
        fsutil.make_dirs(deep_components_path)
        fsutil.make_dirs(atomic_elements_path)

        logger.info(f"Loading font '{font_name}' glifs from database.")

        per_page = settings.ROBOCJK_EXPORT_QUERIES_PAGINATION_LIMIT

        glifs_filters = {}
        if not full_export and updated_after:
            glifs_filters["updated_at__gt"] = updated_after

        character_glyphs_qs = CharacterGlyph.objects.select_related(
            "font", "font__project"
        ).filter(font=font, **glifs_filters)
        character_glyphs_layers_qs = CharacterGlyphLayer.objects.select_related(
            "glif", "glif__font", "glif__font__project"
        ).filter(glif__font=font, **glifs_filters)
        deep_components_qs = DeepComponent.objects.select_related(
            "font", "font__project"
        ).filter(font=font, **glifs_filters)
        atomic_elements_qs = AtomicElement.objects.select_related(
            "font", "font__project"
        ).filter(font=font, **glifs_filters)
        atomic_elements_layers_qs = AtomicElementLayer.objects.select_related(
            "glif", "glif__font", "glif__font__project"
        ).filter(glif__font=font, **glifs_filters)

        character_glyphs_count = character_glyphs_qs.count()
        character_glyphs_layers_count = character_glyphs_layers_qs.count()
        deep_components_count = deep_components_qs.count()
        atomic_elements_count = atomic_elements_qs.count()
        atomic_elements_layers_count = atomic_elements_layers_qs.count()

        # fmt: off
        glifs_count = (
            character_glyphs_count +
            character_glyphs_layers_count +
            deep_components_count +
            atomic_elements_count +
            atomic_elements_layers_count
        )
        # fmt: on
        glifs_progress = 0
        glifs_progress_perc = 0

        glifs_querysets = [
            character_glyphs_qs,
            character_glyphs_layers_qs,
            deep_components_qs,
            atomic_elements_qs,
            atomic_elements_layers_qs,
        ]

        glifs_paginators = [
            Paginator(glifs_queryset, per_page) for glifs_queryset in glifs_querysets
        ]

        # close old database connection to prevent OperationalError(s)
        # (2006, ‘MySQL server has gone away’) and (2013, ‘Lost connection to MySQL server during query’)
        # https://developpaper.com/solution-to-the-lost-connection-problem-of-django-database/
        # close_old_connections()

        num_processes = max(1, (multiprocessing.cpu_count() - 1))

        logger.info(
            f"Saving font '{font_name}' - "
            f"{glifs_count} glifs to file system using {num_processes} process(es)."
        )
        logger.info(f" - {character_glyphs_count} character glyphs")
        logger.info(f" - {character_glyphs_layers_count} character glyphs layers")
        logger.info(f" - {deep_components_count} deep components")
        logger.info(f" - {atomic_elements_count} atomic elements")
        logger.info(f" - {atomic_elements_layers_count} atomic elements layers")

        with multiprocessing.Pool(processes=num_processes) as pool:
            for glifs_paginator in glifs_paginators:
                for glifs_page in glifs_paginator:
                    glifs_list = glifs_page.object_list
                    glifs_data = (
                        (glif.path(), glif.data_formatted) for glif in glifs_list
                    )
                    glifs_files_written_on_disk = pool.map(
                        save_glif_to_file_system, glifs_data
                    )
                    if not all(glifs_files_written_on_disk):
                        logger.exception("Some files were not written to disk.")

                    glifs_progress += len(glifs_list)
                    glifs_progress_perc = (
                        int(round((glifs_progress / glifs_count) * 100))
                        if glifs_count > 0
                        else 0
                    )
                    logger.info(
                        f"Saving font '{font_name}' - "
                        f"{glifs_progress} of {glifs_count} total glifs - {glifs_progress_perc}%"
                    )

        logger.info(f"Verifying font '{font_name}'.")

        # verify existing files with database records

        character_glyphs_qs = (
            CharacterGlyph.objects.select_related("font", "font__project")
            .defer("data")
            .filter(font=font)
        )
        character_glyphs_layers_qs = (
            CharacterGlyphLayer.objects.select_related(
                "glif", "glif__font", "glif__font__project"
            )
            .defer("data")
            .filter(glif__font=font)
        )
        deep_components_qs = (
            DeepComponent.objects.select_related("font", "font__project")
            .defer("data")
            .filter(font=font)
        )
        atomic_elements_qs = (
            AtomicElement.objects.select_related("font", "font__project")
            .defer("data")
            .filter(font=font)
        )
        atomic_elements_layers_qs = (
            AtomicElementLayer.objects.select_related(
                "glif", "glif__font", "glif__font__project"
            )
            .defer("data")
            .filter(glif__font=font)
        )

        glifs_querysets = [
            character_glyphs_qs,
            character_glyphs_layers_qs,
            deep_components_qs,
            atomic_elements_qs,
            atomic_elements_layers_qs,
        ]

        glifs_paginators = [
            Paginator(glifs_queryset, per_page) for glifs_queryset in glifs_querysets
        ]

        glifs_files_expected = set()

        for glifs_paginator in glifs_paginators:
            for glifs_page in glifs_paginator:
                glifs_list = glifs_page.object_list
                glifs_data = (glif.path() for glif in glifs_list)
                glifs_files_expected.update(glifs_data)

        logger.info(
            f"Verifying font '{font_name}' - "
            "comparing .glif objects in database with .glif files on file-system "
            "for checking potential missing and/or zombie files."
        )

        glifs_files_found = set(fsutil.search_files(font_path, "**/*.glif"))
        missing_glifs_files = glifs_files_expected - glifs_files_found
        zombie_glifs_files = glifs_files_found - glifs_files_expected

        if missing_glifs_files:
            missing_glifs_files_count = len(missing_glifs_files)
            missing_glifs_files_str = "\n ".join(missing_glifs_files)
            logger.error(
                f"Verifying font '{font_name}' - "
                f"missing {missing_glifs_files_count} expected glifs files on file system: "
                f"\n {missing_glifs_files_str}"
            )

        if zombie_glifs_files:
            zombie_glifs_files_count = len(zombie_glifs_files)
            zombie_glifs_files_str = "\n ".join(zombie_glifs_files)
            logger.info(
                f"Verifying font '{font_name}' - "
                f"removing {zombie_glifs_files_count} zombie glifs files on file system: "
                f"\n {zombie_glifs_files_str}"
            )
            fsutil.remove_files(*zombie_glifs_files)

        glif_files_pattern = "*.glif"

        def count_glif_files(dirpath):
            return len(fsutil.search_files(dirpath, glif_files_pattern))

        def count_glif_layers_files(dirpath):
            layers_dirs = fsutil.list_dirs(dirpath)
            layers_dirs_glif_files = [
                fsutil.search_files(layer_dir, glif_files_pattern)
                for layer_dir in layers_dirs
            ]
            return sum(
                [len(layer_dir_files) for layer_dir_files in layers_dirs_glif_files]
            )

        def verify_glifs_count(glifs_count, glifs_expected_count, glifs_type_name):
            message = (
                f"Verifying font '{font_name}' - expected {glifs_expected_count}, "
                f"found {glifs_count} {glifs_type_name} .glif files on file-system."
            )
            if glifs_count < glifs_expected_count:
                logger.error(message)
            elif glifs_count == glifs_expected_count:
                logger.info(message)
            elif glifs_count > glifs_expected_count:
                if abs(glifs_expected_count - glifs_count) < 50:
                    message = (
                        f"{message} (some files have been created in the meanwhile)"
                    )
                    logger.info(message)
                elif glifs_expected_count > 0:
                    logger.error(message)

        character_glyphs_count = CharacterGlyph.objects.filter(font=font).count()
        character_glyphs_layers_count = CharacterGlyphLayer.objects.filter(
            glif__font=font
        ).count()
        deep_components_count = DeepComponent.objects.filter(font=font).count()
        atomic_elements_count = AtomicElement.objects.filter(font=font).count()
        atomic_elements_layers_count = AtomicElementLayer.objects.filter(
            glif__font=font
        ).count()

        verify_glifs_count(
            count_glif_files(character_glyphs_path),
            character_glyphs_count,
            "character glyphs",
        )
        verify_glifs_count(
            count_glif_layers_files(character_glyphs_path),
            character_glyphs_layers_count,
            "character glyphs layers",
        )
        verify_glifs_count(
            count_glif_files(deep_components_path),
            deep_components_count,
            "deep components",
        )
        verify_glifs_count(
            count_glif_files(atomic_elements_path),
            atomic_elements_count,
            "atomic elements",
        )
        verify_glifs_count(
            count_glif_layers_files(atomic_elements_path),
            atomic_elements_layers_count,
            "atomic elements layers",
        )

        logger.info(f"Saved font '{font_name}' to file system.")

    def updated_by_users(self, since=None, minutes=None, hours=None, days=None):
        """
        Get the list of users that have updated the font or any object that belongs to it.
        If minutes, hours or days are specified, results will contain only users for the given time range.
        """
        updated_after = None
        if since:
            updated_after = since
        else:
            now = dt.datetime.now()
            if minutes and minutes > 0:
                updated_after = now - dt.timedelta(minutes=minutes)
            elif hours and hours > 0:
                updated_after = now - dt.timedelta(hours=hours)
            elif days and days > 0:
                updated_after = now - dt.timedelta(days=days)
            elif self.export_started_at and self.export_completed_at:
                updated_after = max(self.export_started_at, self.export_completed_at)
            else:
                updated_after = now - dt.timedelta(hours=1)

        def get_updated_by_pks(manager, **filters):
            return (
                manager.exclude(updated_by=None)
                .filter(**filters)
                .order_by("updated_by")
                .values_list("updated_by", flat=True)
                .distinct()
            )

        font = self
        user_manager = get_user_model().objects
        users_pks = []
        users_pks += get_updated_by_pks(manager=Font.objects, uid=font.uid)

        users_pks += get_updated_by_pks(
            manager=GlyphsComposition.objects, font=font, updated_at__gt=updated_after
        )

        users_pks += get_updated_by_pks(
            manager=CharacterGlyph.objects, font=font, updated_at__gt=updated_after
        )

        users_pks += get_updated_by_pks(
            manager=CharacterGlyphLayer.objects.select_related("glif"),
            glif__font=font,
            updated_at__gt=updated_after,
        )

        users_pks += get_updated_by_pks(
            manager=DeepComponent.objects, font=font, updated_at__gt=updated_after
        )

        users_pks += get_updated_by_pks(
            manager=AtomicElement.objects, font=font, updated_at__gt=updated_after
        )

        users_pks += get_updated_by_pks(
            manager=AtomicElementLayer.objects.select_related("glif"),
            glif__font=font,
            updated_at__gt=updated_after,
        )

        users_pks = list(set(users_pks))
        users_qs = user_manager.filter(pk__in=users_pks).order_by(
            "first_name", "last_name"
        )
        return users_qs

    def serialize(self, options=None):
        return serialize_font(self, options)

    def __str__(self):
        return force_str(f"{self.name}")


class FontImport(TimestampModel):
    STATUS_WAITING = "waiting"
    STATUS_LOADING = "loading"
    STATUS_COMPLETED = "completed"
    STATUS_ERROR = "error"
    STATUS_CHOICES = (
        (STATUS_WAITING, _("Waiting")),
        (STATUS_LOADING, _("Loading")),
        (STATUS_COMPLETED, _("Completed")),
        (STATUS_ERROR, _("Error")),
    )

    font = models.ForeignKey(
        "robocjk.Font",
        on_delete=models.CASCADE,
        verbose_name=_("Font"),
    )

    file = models.FileField(
        upload_to="fonts/imports",
        validators=[FileExtensionValidator(allowed_extensions=("zip",))],
        verbose_name=_("File"),
        help_text=_(".zip file containing .rcjk font project."),
    )

    logs = models.TextField(
        blank=True,
        verbose_name=_("Logs"),
    )

    @property
    def filename(self):
        return fsutil.get_filename(self.file.path)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_WAITING,
        db_index=True,
        verbose_name=_("Status"),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Font Import")
        verbose_name_plural = _("Fonts Imports")

    def __str__(self):
        return force_str(f"Font Import [{self.status}]: {self.filename}")


class GlyphsComposition(TimestampModel):
    """
    The Glyphs Composition model.
    """

    class Meta:
        app_label = "robocjk"
        verbose_name = _("Glyphs Composition")
        verbose_name_plural = _("Glyphs Composition")

    font = models.OneToOneField(
        "robocjk.Font",
        null=True,
        on_delete=models.CASCADE,
        related_name="glyphs_composition",
        verbose_name=_("Font"),
    )

    data = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        verbose_name=_("Data"),
    )

    def serialize(self, options=None):
        return self.data or {}

    def __str__(self):
        return force_str("{self.font.name} / {Glyphs Composition}")


class LockableModel(models.Model):
    """
    The Lockable model is an abstract model which provides
    fields and methods to manage glyphs locking/unlocking.
    """

    class Meta:
        abstract = True

    is_locked = models.BooleanField(
        db_index=True,
        default=False,
        verbose_name=_("Is Locked"),
    )

    locked_by = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Locked by"),
    )

    locked_at = models.DateTimeField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Locked at"),
    )

    def _is_valid_user(self, user):
        if not user or user.is_anonymous or not user.is_active:
            return False
        return True

    def lock_by(self, user, save=False):
        if not self._is_valid_user(user):
            return False
        if not self.is_locked:
            # do lock
            self.is_locked = True
            self.locked_by = user
            self.locked_at = dt.datetime.now()
            if save:
                # self.save()
                # don't call save method because it updates the updated_at field timestamp
                glif_model = self.__class__
                glif_model.objects.filter(pk=self.pk).update(
                    is_locked=self.is_locked,
                    locked_by=self.locked_by,
                    locked_at=self.locked_at,
                )
            return True
        return False

    def is_lockable_by(self, user):
        if not self._is_valid_user(user):
            return False
        return False if self.is_locked else True

    def is_locked_by(self, user):
        if not self._is_valid_user(user):
            return False
        return self.locked_by_id == user.id if self.is_locked else False

    def unlock_by(self, user, save=False):
        if not self._is_valid_user(user):
            return False
        if self.is_locked:
            if self.locked_by_id == user.id:
                # do unlock
                self.is_locked = False
                self.locked_by = None
                self.locked_at = None
                if save:
                    # self.save()
                    # don't call save method because it updates the updated_at field timestamp
                    glif_model = self.__class__
                    glif_model.objects.filter(pk=self.pk).update(
                        is_locked=self.is_locked,
                        locked_by=self.locked_by,
                        locked_at=self.locked_at,
                    )
                return True
            return False
        return True


class StatusModel(models.Model):
    """
    The Status model is an abstract model which provides
    status field and state choices.
    """

    class Meta:
        abstract = True

    STATUS_WIP = "wip"
    STATUS_CHECKING_1 = "checking-1"
    STATUS_CHECKING_2 = "checking-2"
    STATUS_CHECKING_3 = "checking-3"
    STATUS_DONE = "done"

    STATUS_DISPLAY_WIP = _("Wip")
    STATUS_DISPLAY_CHECKING_1 = _("Checking 1")
    STATUS_DISPLAY_CHECKING_2 = _("Checking 2")
    STATUS_DISPLAY_CHECKING_3 = _("Checking 3")
    STATUS_DISPLAY_DONE = _("Done")

    STATUS_CHOICES = (
        (
            STATUS_WIP,
            STATUS_DISPLAY_WIP,
        ),
        (
            STATUS_CHECKING_1,
            STATUS_DISPLAY_CHECKING_1,
        ),
        (
            STATUS_CHECKING_2,
            STATUS_DISPLAY_CHECKING_2,
        ),
        (
            STATUS_CHECKING_3,
            STATUS_DISPLAY_CHECKING_3,
        ),
        (
            STATUS_DONE,
            STATUS_DISPLAY_DONE,
        ),
    )
    STATUS_CHOICES_VALUES_LIST = [
        STATUS_WIP,
        STATUS_CHECKING_1,
        STATUS_CHECKING_2,
        STATUS_CHECKING_3,
        STATUS_DONE,
    ]
    STATUS_COLOR_WIP = "#e74c3c"
    STATUS_COLOR_CHECKING_1 = "#e67e22"
    STATUS_COLOR_CHECKING_2 = "#f1c40f"
    STATUS_COLOR_CHECKING_3 = "#2980b9"
    STATUS_COLOR_DONE = "#27ae60"
    STATUS_COLORS = {
        STATUS_WIP: STATUS_COLOR_WIP,  # '#FF0000', # red
        STATUS_CHECKING_1: STATUS_COLOR_CHECKING_1,  # '#FF8800', # orange
        STATUS_CHECKING_2: STATUS_COLOR_CHECKING_2,  # '#FFFF00', # yellow
        STATUS_CHECKING_3: STATUS_COLOR_CHECKING_3,  # '#0088FF', # blue
        STATUS_DONE: STATUS_COLOR_DONE,  # '#00FF88', # green
    }
    STATUS_MARK_COLORS = {
        "1,0,0,1": STATUS_WIP,
        "1,0.5,0,1": STATUS_CHECKING_1,
        "1,1,0,1": STATUS_CHECKING_2,
        "0,0.5,1,1": STATUS_CHECKING_3,
        "0,1,0.5,1": STATUS_DONE,
    }

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_WIP,
        db_index=True,
        verbose_name=_("Status"),
    )

    status_changed_at = models.DateTimeField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Status changed at"),
    )

    previous_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_WIP,
        db_index=True,
        verbose_name=_("Previous status"),
    )

    status_downgraded = models.BooleanField(
        default=False,
        verbose_name=_("Status downgraded"),
    )

    status_downgraded_at = models.DateTimeField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Status downgraded at"),
    )

    @property
    def status_color(self):
        return StatusModel.STATUS_COLORS.get(self.status, "#CCCCCC")

    @staticmethod
    def get_status_from_data(data):
        status = None
        # new status format 2021/09: public.markColor -> robocjk.status
        status_index = data.status
        if status_index is not None:
            status = StatusModel.STATUS_CHOICES[status_index][0]
        # old status format fallback
        if status is None:
            status_color = data.status_color
            if status_color:
                status = StatusModel.STATUS_MARK_COLORS.get(status_color, None)
        # default status fallback
        if status is None:
            status = StatusModel.STATUS_WIP
        return status


class GlifDataModel(models.Model):
    """
    The GlifData model is an abstract model which parses xml data
    from .glif files and extract property values for fast lookup.
    """

    class Meta:
        abstract = True

    deleted = models.BooleanField(
        default=False,
        verbose_name=_("Deleted"),
    )

    data = models.TextField(
        verbose_name=_("Data"),
        help_text=_("(.glif xml data)"),
    )

    @property
    def data_formatted(self):
        try:
            s = format_glif(self.data)
        except Exception as formatting_error:
            s = self.data
            message = "glif xml data formatting error - pk: {}, error: {}".format(
                self.pk, formatting_error
            )
            # print(message)
            logger.exception(message)
        return s

    name = models.CharField(
        blank=True,
        max_length=50,
        db_index=True,
        verbose_name=_("Name"),
        help_text=_("(autodetected from xml data)"),
    )

    filename = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Filename"),
        help_text=_("(.glif xml output filename, autodetected from xml data)"),
    )

    unicode_hex = models.CharField(
        db_index=True,
        max_length=50,
        blank=True,
        default="",
        verbose_name=_("Unicode hex"),
        help_text=_("(unicode hex value, autodetected from xml data)"),
    )

    components = models.TextField(
        blank=True,
        verbose_name=_("Components"),
    )

    @property
    def components_names(self):
        return list(filter(None, self.components.split(",")))

    def get_components_managers(self):
        return None

    # empty means that there is no deep components instance inside, and no contours and not flat components
    is_empty = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Is Empty"),
        help_text=_("(autodetected from xml data)"),
    )

    has_variation_axis = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Has Variation Axis"),
        help_text=_("(autodetected from xml data)"),
    )

    has_outlines = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Has Outlines"),
        help_text=_("(autodetected from xml data)"),
    )

    has_components = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Has Components"),
        help_text=_("(autodetected from xml data)"),
    )

    has_unicode = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Has Unicode"),
        help_text=_("(autodetected from xml data)"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_data = None

    @property
    def unicodes_hex(self):
        return unicodes_str_to_list(self.unicode_hex, to_int=False)

    @property
    def unicodes_int(self):
        return unicodes_str_to_list(self.unicode_hex, to_int=True)

    def _parse_data(self, data_str):
        if data_str:
            gliph_data = GlifData()
            gliph_data.parse_string(data_str)
            if gliph_data.ok:
                return gliph_data
            else:
                logger.exception(
                    f"{self.__class__} - parse data error: {gliph_data.error}"
                )
                return None
        return None

    def _apply_data(self, data):
        if not data:
            return

        self._update_init_data()

        self.data = data.xml_string
        self.name = data.name
        self.filename = data.filename
        self.unicode_hex = data.unicode_hex
        self.is_empty = data.is_empty
        self.has_variation_axis = data.has_variation_axis
        self.has_outlines = data.has_outlines
        self.has_components = data.has_components
        self.has_unicode = data.has_unicode
        self.components = data.components_str

    def _update_init_data(self):
        if not self._init_data:
            self._init_data = self.data

    def _update_status(self, glif_data):  # noqa: C901
        if not glif_data:
            # invalid glif data
            return

        if not isinstance(
            self,
            (
                CharacterGlyph,
                DeepComponent,
                AtomicElement,
            ),
        ):
            # glif layers have not status
            return

        self._update_init_data()

        if self.data == self._init_data:
            # data is not changed
            return

        if self._init_data:
            # it is not the first save/creation
            init_glif_data = self._parse_data(self._init_data)
            if init_glif_data:
                any_status_downgraded = False
                any_status_upgraded = False
                if (
                    init_glif_data.status_with_variations
                    != glif_data.status_with_variations
                ):
                    # some status changed, check if any status has been downgraded
                    for key, val in glif_data.status_with_variations.items():
                        init_val = (
                            init_glif_data.status_with_variations.get(key, 0) or 0
                        )
                        # flag as downgraded when any source changes from done to a previous status
                        if init_val == 4 and val < init_val:
                            any_status_downgraded = True
                        # deflag downgraded when any source changes to done
                        if init_val < 4 and val == 4:
                            any_status_upgraded = True

                if any_status_downgraded:
                    if not self.status_downgraded:
                        self.status_downgraded = True
                        self.status_downgraded_at = dt.datetime.now()
                elif any_status_upgraded:
                    if self.status_downgraded:
                        self.status_downgraded = False
                        self.status_downgraded_at = None

        # update init data to avoid to re-compute downgrade/upgrade
        # on possibile subsequent save calls on the same instance
        self._init_data = self.data

        # this should be removed because not useful for detecting variations downgrades
        data_status = StatusModel.get_status_from_data(glif_data)
        # print(data_status)
        if self.status != data_status:
            self.previous_status = self.status
            self.status = data_status
            self.status_changed_at = dt.datetime.now()

    def _update_components(self):
        if self.has_components:
            comp_managers = self.get_components_managers()
            if not comp_managers:
                return False
            for comp_manager in comp_managers:
                comp_set = comp_manager[0]
                comp_cls = comp_manager[1]
                comp_names = self.components_names
                # logger.debug(comp_names)
                if comp_names:
                    comp_set.clear()
                    comp_objs = comp_cls.objects.filter(
                        font_id=self.font_id, name__in=comp_names
                    )
                    # logger.debug(comp_objs)
                    comp_set.add(*comp_objs)
                else:
                    comp_set.clear()
            return True
        return False

    def update_components(self):
        self._update_components()

    def path(self):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        self._update_init_data()
        glif_data = self._parse_data(self.data)
        self._apply_data(glif_data)
        self._update_status(glif_data)
        super().save(*args, **kwargs)
        # update many-to-many relations after the instance has been saved
        self._update_components()

    def save_to_file_system(self):
        # this method is not actually used
        filepath = self.path()
        fsutil.write_file(filepath, self.data_formatted)
        # logger.debug('save_to_file_system glif filepath: {} - exists: {}'.format(filepath, fsutil.exists(filepath)))

    def delete_from_file_system(self):
        try:
            filepath = self.path()
        except ObjectDoesNotExist:
            # this happens is rare circumstances when
            # this method is called on an in-memory zombie glif.
            # eg. glif deleted via api after it has been loaded
            # from the database during the export process
            pass
        else:
            if fsutil.is_file(filepath):
                fsutil.remove_file(filepath)


class DeletedGlif(models.Model):
    GLIF_TYPE_ATOMIC_ELEMENT = "atomic_element"
    GLIF_TYPE_ATOMIC_ELEMENT_LAYER = "atomic_element_layer"
    GLIF_TYPE_DEEP_COMPONENT = "deep_component"
    GLIF_TYPE_CHARACTER_GLYPH = "character_glyph"
    GLIF_TYPE_CHARACTER_GLYPH_LAYER = "character_glyph_layer"

    GLIF_TYPE_CHOICES = (
        (GLIF_TYPE_ATOMIC_ELEMENT, _("Atomic Element")),
        (GLIF_TYPE_ATOMIC_ELEMENT_LAYER, _("Atomic Element Layer")),
        (GLIF_TYPE_DEEP_COMPONENT, _("Deep Component")),
        (GLIF_TYPE_CHARACTER_GLYPH, _("Character Glyph")),
        (GLIF_TYPE_CHARACTER_GLYPH_LAYER, _("Character Glyph Layer")),
    )

    GLIF_TYPES = (
        GLIF_TYPE_ATOMIC_ELEMENT,
        GLIF_TYPE_ATOMIC_ELEMENT_LAYER,
        GLIF_TYPE_DEEP_COMPONENT,
        GLIF_TYPE_CHARACTER_GLYPH,
        GLIF_TYPE_CHARACTER_GLYPH_LAYER,
    )

    @classmethod
    def get_glif_type_by_glif(cls, glif):
        if isinstance(glif, AtomicElement):
            return cls.GLIF_TYPE_ATOMIC_ELEMENT
        elif isinstance(glif, AtomicElementLayer):
            return cls.GLIF_TYPE_ATOMIC_ELEMENT_LAYER
        elif isinstance(glif, DeepComponent):
            return cls.GLIF_TYPE_DEEP_COMPONENT
        elif isinstance(glif, CharacterGlyph):
            return cls.GLIF_TYPE_CHARACTER_GLYPH
        elif isinstance(glif, CharacterGlyphLayer):
            return cls.GLIF_TYPE_CHARACTER_GLYPH_LAYER
        else:
            raise ValueError(f"Invalid glif: {glif}")

    class Meta:
        app_label = "robocjk"
        verbose_name = _("Deleted Glif")
        verbose_name_plural = _("Deleted Glifs")

    deleted_at = models.DateTimeField(
        verbose_name=_("Deleted at"),
    )
    deleted_by = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Deleted by"),
    )
    font = models.ForeignKey(
        "robocjk.Font",
        on_delete=models.CASCADE,
        related_name="deleted_glifs",
        verbose_name=_("Font"),
    )
    glif_type = models.CharField(
        db_index=True,
        max_length=50,
        choices=GLIF_TYPE_CHOICES,
        verbose_name=_("Glif Type"),
    )
    glif_id = models.PositiveIntegerField(
        db_index=True,
        verbose_name=_("Glif ID"),
    )
    group_name = models.CharField(
        db_index=True,
        blank=True,
        max_length=50,
        verbose_name=_("Group Name"),
    )
    name = models.CharField(
        db_index=True,
        blank=True,
        max_length=50,
        verbose_name=_("Name"),
    )
    filename = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Filename"),
    )
    filepath = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Filepath"),
    )

    def __str__(self):
        return force_str(f"[{self.glif_type}] {self.glif_id}")


class CharacterGlyph(GlifDataModel, StatusModel, LockableModel, TimestampModel):
    class Meta:
        app_label = "robocjk"
        # ordering = ['name']
        unique_together = [
            ["font", "name"],
        ]
        verbose_name = _("Character Glyph")
        verbose_name_plural = _("Character Glyphs")

    font = models.ForeignKey(
        "robocjk.Font",
        on_delete=models.CASCADE,
        related_name="character_glyphs",
        verbose_name=_("Font"),
    )

    character_glyphs = models.ManyToManyField(
        "robocjk.CharacterGlyph",
        blank=True,
        related_name="used_by_character_glyphs",
        verbose_name=_("Character Glyphs"),
    )

    deep_components = models.ManyToManyField(
        "robocjk.DeepComponent",
        blank=True,
        related_name="character_glyphs",
        verbose_name=_("Deep Components"),
    )

    layers_updated_at = models.DateTimeField(
        blank=True,
        null=True,
        default=None,
        editable=False,
        verbose_name=_("Layers updated at"),
    )

    objects = CharacterGlyphManager()

    def get_components_managers(self):
        return (
            (
                self.character_glyphs,
                CharacterGlyph,
            ),
            (
                self.deep_components,
                DeepComponent,
            ),
        )

    def path(self):
        return get_character_glyph_path(self)

    def serialize(self, options=None):
        return serialize_character_glyph(self, options)

    def update_layers_updated_at(self):
        layers_updated_at_max = self.layers.aggregate(Max("updated_at"))[
            "updated_at__max"
        ]
        layers_deleted_at_max = DeletedGlif.objects.filter(
            glif_type=DeletedGlif.GLIF_TYPE_CHARACTER_GLYPH_LAYER,
            glif_id=self.id,
        ).aggregate(Max("deleted_at"))["deleted_at__max"]

        # compute max layers_updated_at value
        layers_updated_at = None
        if layers_updated_at_max and layers_deleted_at_max:
            layers_updated_at = max(layers_updated_at_max, layers_deleted_at_max)
        else:
            layers_updated_at = layers_updated_at_max or layers_deleted_at_max

        # update in-memory value
        self.layers_updated_at = layers_updated_at

        # update database value
        cls = self.__class__
        cls.objects.filter(pk=self.pk).update(layers_updated_at=layers_updated_at)

    def __str__(self):
        return force_str(f"{self.name}")


class CharacterGlyphLayer(GlifDataModel, TimestampModel):
    class Meta:
        app_label = "robocjk"
        # ordering = ['group_name']
        unique_together = [
            ["glif", "group_name", "name"],
        ]
        verbose_name = _("Character Glyph Layer")
        verbose_name_plural = _("Character Glyph Layers")

    glif = models.ForeignKey(
        "robocjk.CharacterGlyph",
        on_delete=models.CASCADE,
        related_name="layers",
        verbose_name=_("Glif"),
    )

    group_name = models.CharField(
        db_index=True,
        max_length=50,
        verbose_name=_("Group Name"),
    )

    objects = CharacterGlyphLayerManager()

    @property
    def font(self):
        return self.glif.font

    def path(self):
        return get_character_glyph_layer_path(self)

    def rename(self, new_group_name):
        if self.group_name == new_group_name:
            return
        self.delete_from_file_system()
        self.group_name = new_group_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.glif.update_layers_updated_at()

    def serialize(self, options=None):
        return serialize_character_glyph_layer(self, options)

    def __str__(self):
        return force_str(f"[{self.group_name}] {self.name}")


class DeepComponent(GlifDataModel, StatusModel, LockableModel, TimestampModel):
    class Meta:
        app_label = "robocjk"
        # ordering = ['name']
        unique_together = [
            ["font", "name"],
        ]
        verbose_name = _("Deep Component")
        verbose_name_plural = _("Deep Components")

    font = models.ForeignKey(
        "robocjk.Font",
        on_delete=models.CASCADE,
        related_name="deep_components",
        verbose_name=_("Font"),
    )

    atomic_elements = models.ManyToManyField(
        "robocjk.AtomicElement",
        blank=True,
        related_name="deep_components",
        verbose_name=_("Atomic Elements"),
    )

    objects = DeepComponentManager()

    def get_components_managers(self):
        return (
            (
                self.atomic_elements,
                AtomicElement,
            ),
        )

    def path(self):
        return get_deep_component_path(self)

    def serialize(self, options=None):
        return serialize_deep_component(self, options)

    def __str__(self):
        return force_str(f"{self.name}")


class AtomicElement(GlifDataModel, StatusModel, LockableModel, TimestampModel):
    class Meta:
        app_label = "robocjk"
        # ordering = ['name']
        unique_together = [
            ["font", "name"],
        ]
        verbose_name = _("Atomic Element")
        verbose_name_plural = _("Atomic Elements")

    font = models.ForeignKey(
        "robocjk.Font",
        on_delete=models.CASCADE,
        related_name="atomic_elements",
        verbose_name=_("Font"),
    )

    layers_updated_at = models.DateTimeField(
        blank=True,
        null=True,
        default=None,
        editable=False,
        verbose_name=_("Layers updated at"),
    )

    objects = AtomicElementManager()

    def path(self):
        return get_atomic_element_path(self)

    def serialize(self, options=None):
        return serialize_atomic_element(self, options)

    def update_layers_updated_at(self):
        layers_updated_at_max = self.layers.aggregate(Max("updated_at"))[
            "updated_at__max"
        ]
        layers_deleted_at_max = DeletedGlif.objects.filter(
            glif_type=DeletedGlif.GLIF_TYPE_ATOMIC_ELEMENT_LAYER,
            glif_id=self.id,
        ).aggregate(Max("deleted_at"))["deleted_at__max"]

        # compute max layers_updated_at value
        layers_updated_at = None
        if layers_updated_at_max and layers_deleted_at_max:
            layers_updated_at = max(layers_updated_at_max, layers_deleted_at_max)
        else:
            layers_updated_at = layers_updated_at_max or layers_deleted_at_max

        # update in-memory value
        self.layers_updated_at = layers_updated_at

        # update database value
        cls = self.__class__
        cls.objects.filter(pk=self.pk).update(layers_updated_at=layers_updated_at)

    def __str__(self):
        return force_str(f"{self.name}")


class AtomicElementLayer(GlifDataModel, TimestampModel):
    class Meta:
        app_label = "robocjk"
        # ordering = ['group_name']
        unique_together = [
            ["glif", "group_name", "name"],
        ]
        verbose_name = _("Atomic Element Layer")
        verbose_name_plural = _("Atomic Element Layers")

    glif = models.ForeignKey(
        "robocjk.AtomicElement",
        on_delete=models.CASCADE,
        related_name="layers",
        verbose_name=_("Glif"),
    )

    group_name = models.CharField(
        db_index=True,
        max_length=50,
        verbose_name=_("Group Name"),
    )

    objects = AtomicElementLayerManager()

    @property
    def font(self):
        return self.glif.font

    def path(self):
        return get_atomic_element_layer_path(self)

    def rename(self, new_group_name):
        if self.group_name == new_group_name:
            return
        self.delete_from_file_system()
        self.group_name = new_group_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.glif.update_layers_updated_at()

    def serialize(self, options=None):
        return serialize_atomic_element_layer(self, options)

    def __str__(self):
        return force_str(f"[{self.group_name}] {self.name}")


class Proof(TimestampModel):
    class Meta:
        app_label = "robocjk"
        ordering = ["-updated_at"]
        verbose_name = _("Proof")
        verbose_name_plural = _("Proofs")

    FILETYPE_PDF = "pdf"
    FILETYPE_MP4 = "mp4"
    FILETYPE_CHOICES = (
        (
            FILETYPE_PDF,
            _(".pdf"),
        ),
        (
            FILETYPE_MP4,
            _(".mp4"),
        ),
    )

    font = models.ForeignKey(
        "robocjk.Font",
        on_delete=models.CASCADE,
        related_name="proofs",
        verbose_name=_("Font"),
    )

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )

    filetype = models.CharField(
        max_length=10,
        choices=FILETYPE_CHOICES,
        verbose_name=_("Filetype"),
    )

    file = models.FileField(
        upload_to="proofs",
        validators=[
            FileExtensionValidator(
                allowed_extensions=(
                    "pdf",
                    "mp4",
                )
            )
        ],
        verbose_name=_("File"),
    )

    def path(self):
        return get_proof_path(self)

    def __str__(self):
        return force_str(f"[{self.get_filetype_display()}] {self.file}")


connect_signals()
