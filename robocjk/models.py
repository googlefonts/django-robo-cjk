# -*- coding: utf-8 -*-

from benedict import benedict
from benedict.serializers import Base64Serializer

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str

from robocjk.abstract_models import (
    UIDModel, HashidModel, NameSlugModel, TimestampModel, ExportModel,
)
from robocjk.api.serializers import (
    serialize_project,
    serialize_font,
    serialize_atomic_element,
    serialize_atomic_element_layer,
    serialize_deep_component,
    serialize_character_glyph,
    serialize_character_glyph_layer,
)
from robocjk.core import GlifData
from robocjk.debug import logger
from robocjk.io.paths import (
    get_project_path,
    get_font_path,
    get_character_glyphs_path,
    get_character_glyph_path,
    get_character_glyph_layer_path,
    get_deep_components_path,
    get_deep_component_path,
    get_atomic_elements_path,
    get_atomic_element_path,
    get_atomic_element_layer_path,
    get_proof_path,
)
from robocjk.managers import (
    ProjectManager,
    FontManager,
    CharacterGlyphManager, CharacterGlyphLayerManager,
    DeepComponentManager,
    AtomicElementManager, AtomicElementLayerManager,
)
from robocjk.utils import format_glif
from robocjk.validators import GitSSHRepositoryURLValidator

import datetime as dt
import fsutil
import multiprocessing
import os
import time


"""
1. “atomic elements” contain only outlines, not references to other atomic elements
2. “deep components” contain only references to atomic elements, and do not contain outlines
3. “character glyphs”, contain only references to deep components, not to atomic elements, and outlines
"""


def run_commands(*args):
    cmds = args
    cmd = ' && '.join(cmds)
    logger.info('Run system commands: \n{}'.format(cmd))
    os.system(cmd)


class Project(UIDModel, HashidModel, NameSlugModel, TimestampModel, ExportModel):
    """
    The Project model.
    """
    class Meta:
        app_label = 'robocjk'
        ordering = ['name']
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')

    repo_url = models.CharField(
        unique=True,
        max_length=200,
        validators=[GitSSHRepositoryURLValidator()],
        verbose_name=_('Repo URL'),
        help_text=_('The .git repository SSH URL, eg. git@github.com:username/repository.git'))

    designers = models.ManyToManyField(
        get_user_model(),
        blank=True,
        related_name='projects',
        verbose_name=_('Designers'))

    objects = ProjectManager()

    def num_designers(self):
        return self.designers.count()

    def num_fonts(self):
        return self.fonts.count()

    def path(self):
        return get_project_path(self)

    def save_to_file_system(self):
        logger.info('Saving project "{}" to file system...'.format(self.name))
        path = self.path()
        fsutil.make_dirs(path)
        repo_path = fsutil.join_path(path, '.git')
        if not fsutil.exists(repo_path):
            # repository doesn't exist, initialize it
            logger.info('Repository for project "{}" doesn\'t exist, initialize it.'.format(self.name))
            run_commands(
                'cd {}'.format(path),
                'git init',
                'git config --local --add "user.name" "{}"'.format(settings.GIT_USER_NAME),
                'git config --local --add "user.email" "{}"'.format(settings.GIT_USER_EMAIL),
                'git remote add origin {}'.format(self.repo_url),
                'git pull origin master')
        else:
            # repository exist
            logger.info('Repository for project "{}" already exist, update it.'.format(self.name))
            run_commands(
                'cd {}'.format(path),
                'git reset --hard origin/master',
                'git pull origin master',
                'git clean -df')
        # save all project fonts to file.system
        fonts_qs = self.fonts.prefetch_related(
            'character_glyphs',
            'character_glyphs__layers',
            'deep_components',
            'atomic_elements',
            'atomic_elements__layers').filter()
        fonts_list = list(fonts_qs)
        # cleanup - remove .rcjk projects that don't belong anymore to a project font
        fonts_rcjk_pulled_dirs = set(fsutil.search_dirs(path, '*.rcjk'))
        fonts_rcjk_dirs = {font.path() for font in fonts_list}
        fonts_rcjk_deleted_dirs = list(fonts_rcjk_pulled_dirs - fonts_rcjk_dirs)
        logger.info('Deleting project "{}" old fonts from file system...\n{}'.format(self.name, fonts_rcjk_deleted_dirs))
        fsutil.remove_dirs(*fonts_rcjk_deleted_dirs)
        # save all project fonts to the file system
        logger.info('Saving project "{}" fonts to file system...\n{}'.format(self.name, [font.name for font in fonts_list]))
        for font in fonts_list:
            font_dirpath = fsutil.get_filename(font.path())
            font_commit_message = font.get_commit_message()
            font.export()
            # add all changed files, commit and push to the git repository
            run_commands(
                'cd {}'.format(path),
                'git add ./{}'.format(font_dirpath),
                'git commit -m "{}"'.format(font_commit_message),
                'git push origin master')
        run_commands(
            'cd {}'.format(path),
            'git add --all',
            'git commit -m "{}"'.format('Updated project.'),
            'git push origin master')

    def serialize(self, **kwargs):
        return serialize_project(self, **kwargs)

    def __str__(self):
        return force_str('{}'.format(
            self.name))


def save_glif_to_file_system_async(glif):
    """
    Worker function for saving glif files to file-system asyncronously.
    """
    # logger.debug('Saving glif "{}" to file system: {}'.format(glif, glif.path()))
    glif.save_to_file_system()


class Font(UIDModel, HashidModel, NameSlugModel, TimestampModel, ExportModel):
    """
    The Font model.
    """
    class Meta:
        app_label = 'robocjk'
        ordering = ['name']
        verbose_name = _('Font')
        verbose_name_plural = _('Fonts')

    project = models.ForeignKey(
        'robocjk.Project',
        on_delete=models.CASCADE,
        related_name='fonts',
        verbose_name=_('Project'))

    available = models.BooleanField(
        db_index=True,
        default=True,
        verbose_name=_('Available'))

    fontlib = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        verbose_name=_('FontLib'))

    features = models.TextField(
        blank=True,
        verbose_name=_('Features'))

    designspace = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        verbose_name=_('Designspace'))

    objects = FontManager()

    def get_commit_message(self, **options):
        """
        Get the commit message for the font combining the font name and
        the list of users that worked on it since the last project export).
        """
        users_qs = self.updated_by_users(**options)
        users_names = [user.get_full_name() for user in users_qs]
        users_str = ', '.join(users_names)
        # return 'Updated {}.'.format(self.name)
        message = 'Updated {}'.format(self.name)
        if users_str:
            return '{} by: {}.'.format(message, users_str)
        return '{}.'.format(message)

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

    def save_to_file_system(self):
        font = self
        if not font.available:
            logger.info('Skipped font "{}" saving because it is not available (maybe there is an import running).'.format(font.name))
            return
        logger.info('Saving font "{}" to file system...'.format(font.name))
        path = font.path()
        fsutil.make_dirs(path)
        # write fontLib.json file
        logger.info('Saving font "{}" "fontLib.json" to file system...'.format(font.name))
        fontlib_path = fsutil.join_path(path, 'fontLib.json')
        fontlib_str = benedict(font.fontlib, keypath_separator=None).dump()
        fsutil.write_file(fontlib_path, fontlib_str)
        # write features.fea file
        logger.info('Saving font "{}" "features.fea" to file system...'.format(font.name))
        features_path = fsutil.join_path(path, 'features.fea')
        fsutil.write_file(features_path, font.features)
        # write designspace.json file
        logger.info('Saving font "{}" "designspace.json" to file system...'.format(font.name))
        designspace_path = fsutil.join_path(path, 'designspace.json')
        designspace_str = benedict(font.designspace, keypath_separator=None).dump()
        fsutil.write_file(designspace_path, designspace_str)
        # write glyphsComposition.json file
        logger.info('Saving font "{}" "glyphsComposition.json" to file system...'.format(font.name))
        glyphs_composition_obj, _ = GlyphsComposition.objects.get_or_create(font_id=font.id)
        glyphs_composition_path = fsutil.join_path(path, 'glyphsComposition.json')
        glyphs_composition_str = benedict(glyphs_composition_obj.serialize(), keypath_separator=None).dump()
        fsutil.write_file(glyphs_composition_path, glyphs_composition_str)
        # delete existing character-glyphs, deep-components and atomic-elements directories
        logger.info('Deleting font "{}" character-glyphs, deep-components and atomic-elements folders...'.format(font.name))

        character_glyphs_path = get_character_glyphs_path(font)
        deep_components_path = get_deep_components_path(font)
        atomic_elements_path = get_atomic_elements_path(font)
        fsutil.remove_dirs(
            character_glyphs_path,
            deep_components_path,
            atomic_elements_path)

        logger.info('Loading font "{}" glif objects in memory...'.format(font.name))
        t = time.time()
        # load all character-glyphs
        character_glyphs_qs = CharacterGlyph.objects.select_related('font', 'font__project').filter(font=font) # select_related('font', 'font__project')
        character_glyphs_list = list(character_glyphs_qs)
        # load all character-glyphs-layers
        character_glyphs_layers_qs = CharacterGlyphLayer.objects.select_related('glif__font', 'glif__font__project').filter(glif__font=font)
        character_glyphs_layers_list = list(character_glyphs_layers_qs)
        # load all deep-components
        deep_components_qs = DeepComponent.objects.select_related('font', 'font__project').filter(font=font)
        deep_components_list = list(deep_components_qs)
        # load all atomic-elements
        atomic_elements_qs = AtomicElement.objects.select_related('font', 'font__project').filter(font=font)
        atomic_elements_list = list(atomic_elements_qs)
        # load all atomic-elements-layers
        atomic_elements_layers_qs = AtomicElementLayer.objects.select_related('glif__font', 'glif__font__project').filter(glif__font=font)
        atomic_elements_layers_list = list(atomic_elements_layers_qs)
        # load complete
        logger.info('Loaded font "{}" glif objects in memory in {} seconds.'.format(font, time.time() - t))

        logger.info('Saving font "{}" ({} character glyphs, {} character glyphs layers, {} deep components, {} atomic elements, {} atomic elements layers) to file system...'.format(
            font.name,
            len(character_glyphs_list),
            len(character_glyphs_layers_list),
            len(deep_components_list),
            len(atomic_elements_list),
            len(atomic_elements_layers_list)
        ))

        glifs_list = character_glyphs_list + character_glyphs_layers_list + deep_components_list + atomic_elements_list + atomic_elements_layers_list

#         # sync solution
#         glif_counter = 0
#         glif_count = len(glifs_list)
#         for glif_obj in glifs_list:
#             glif_obj.save_to_file_system()
#             glif_counter += 1
#             # logger.debug('Saving font "{}" glif {} of {} to file system: {}'.format(font.name, glif_counter, glif_count, glif_obj.path()))

        # async solution with native multiprocessing
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            result = pool.map(save_glif_to_file_system_async, glifs_list)

        logger.info('Saved font "{}" to file system.'.format(font.name))

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
            filters.setdefault('updated_at__gt', updated_after)
            return manager.filter(**filters) \
                .exclude(updated_by=None) \
                .order_by('updated_by') \
                .values_list('updated_by', flat=True) \
                .distinct()

        font = self
        user_manager = get_user_model().objects
        users_pks = []
        users_pks += get_updated_by_pks(
            manager=Font.objects,
            uid=font.uid)

        users_pks += get_updated_by_pks(
            manager=GlyphsComposition.objects,
            font=font)

        users_pks += get_updated_by_pks(
            manager=CharacterGlyph.objects,
            font=font)

        users_pks += get_updated_by_pks(
            manager=CharacterGlyphLayer.objects.select_related('glif'),
            glif__font=font)

        users_pks += get_updated_by_pks(
            manager=DeepComponent.objects,
            font=font)

        users_pks += get_updated_by_pks(
            manager=AtomicElement.objects,
            font=font)

        users_pks += get_updated_by_pks(
            manager=AtomicElementLayer.objects.select_related('glif'),
            glif__font=font)

        users_pks = list(set(users_pks))
        users_qs = user_manager.filter(pk__in=users_pks).order_by('first_name', 'last_name')
        return users_qs

    def serialize(self, **kwargs):
        return serialize_font(self, **kwargs)

    def __str__(self):
        return force_str('{}'.format(
            self.name))


class FontImport(TimestampModel):

    STATUS_WAITING = 'waiting'
    STATUS_LOADING = 'loading'
    STATUS_COMPLETED = 'completed'
    STATUS_ERROR = 'error'
    STATUS_CHOICES = (
        (STATUS_WAITING, _('Waiting'), ),
        (STATUS_LOADING, _('Loading'), ),
        (STATUS_COMPLETED, _('Completed'), ),
        (STATUS_ERROR, _('Error'), ),
    )

    font = models.ForeignKey(
        'robocjk.Font',
        on_delete=models.CASCADE,
        verbose_name=_('Font'))

    file = models.FileField(
        upload_to='fonts/imports',
        validators=[FileExtensionValidator(
            allowed_extensions=('zip', ))],
        verbose_name=_('File'),
        help_text=_('.zip file containing .rcjk font project.'))

    logs = models.TextField(
        blank=True,
        verbose_name=_('Logs'))

    @property
    def filename(self):
        return fsutil.get_filename(self.file.path)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_WAITING,
        db_index=True,
        verbose_name=_('Status'))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Font Import')
        verbose_name_plural = _('Fonts Imports')

    def __str__(self):
        return force_str('{} [{}]: {}'.format(
            _('Font Import'),
            self.status,
            self.filename))


class GlyphsComposition(TimestampModel):
    """
    The Glyphs Composition model.
    """
    class Meta:
        app_label = 'robocjk'
        verbose_name = _('Glyphs Composition')
        verbose_name_plural = _('Glyphs Composition')

    font = models.OneToOneField(
        'robocjk.Font',
        null=True,
        on_delete=models.CASCADE,
        related_name='glyphs_composition',
        verbose_name=_('Font'))

    data = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        verbose_name=_('Data'))

    def serialize(self, **kwargs):
        return self.data or {}

    def __str__(self):
        return force_str('{} / {}'.format(
            self.font.name,
            _('Glyphs Composition')))


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
        verbose_name=_('Is Locked'))

    locked_by = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Locked by'))

    locked_at = models.DateTimeField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Locked at'))

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
                self.save()
            return True
        return self.locked_by_id == user.id

    def is_lockable_by(self, user):
        if not self._is_valid_user(user):
            return False
        return self.locked_by_id == user.id if self.is_locked else True

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
                    self.save()
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

    STATUS_WIP = 'wip'
    STATUS_CHECKING_1 = 'checking-1'
    STATUS_CHECKING_2 = 'checking-2'
    STATUS_CHECKING_3 = 'checking-3'
    STATUS_DONE = 'done'

    STATUS_DISPLAY_WIP = _('Wip')
    STATUS_DISPLAY_CHECKING_1 = _('Checking 1')
    STATUS_DISPLAY_CHECKING_2 = _('Checking 2')
    STATUS_DISPLAY_CHECKING_3 = _('Checking 3')
    STATUS_DISPLAY_DONE = _('Done')

    STATUS_CHOICES = (
        (STATUS_WIP, STATUS_DISPLAY_WIP, ),
        (STATUS_CHECKING_1, STATUS_DISPLAY_CHECKING_1, ),
        (STATUS_CHECKING_2, STATUS_DISPLAY_CHECKING_2, ),
        (STATUS_CHECKING_3, STATUS_DISPLAY_CHECKING_3, ),
        (STATUS_DONE, STATUS_DISPLAY_DONE, ),
    )
    STATUS_CHOICES_VALUES_LIST = [
        STATUS_WIP,
        STATUS_CHECKING_1,
        STATUS_CHECKING_2,
        STATUS_CHECKING_3,
        STATUS_DONE,
    ]
    STATUS_COLOR_WIP = '#e74c3c'
    STATUS_COLOR_CHECKING_1 = '#e67e22'
    STATUS_COLOR_CHECKING_2 = '#f1c40f'
    STATUS_COLOR_CHECKING_3 = '#2980b9'
    STATUS_COLOR_DONE = '#27ae60'
    STATUS_COLORS = {
        STATUS_WIP: STATUS_COLOR_WIP, # '#FF0000', # red
        STATUS_CHECKING_1: STATUS_COLOR_CHECKING_1, # '#FF8800', # orange
        STATUS_CHECKING_2: STATUS_COLOR_CHECKING_2, # '#FFFF00', # yellow
        STATUS_CHECKING_3: STATUS_COLOR_CHECKING_3, # '#0088FF', # blue
        STATUS_DONE: STATUS_COLOR_DONE, # '#00FF88', # green
    }
    STATUS_MARK_COLORS = {
        '1,0,0,1': STATUS_WIP,
        '1,0.5,0,1': STATUS_CHECKING_1,
        '1,1,0,1': STATUS_CHECKING_2,
        '0,0.5,1,1': STATUS_CHECKING_3,
        '0,1,0.5,1': STATUS_DONE,
    }
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_WIP,
        db_index=True,
        verbose_name=_('Status'))

    @property
    def status_color(self):
        return StatusModel.STATUS_COLORS.get(
            self.status, '#CCCCCC')


class GlifDataModel(models.Model):
    """
    The GlifData model is an abstract model which parses xml data
    from .glif files and extract property values for fast lookup.
    """
    class Meta:
        abstract = True

    data = models.TextField(
        verbose_name=_('Data'),
        help_text=_('(.glif xml data)'))

    name = models.CharField(
        blank=True,
        max_length=50,
        db_index=True,
        verbose_name=_('Name'),
        help_text=_('(autodetected from xml data)'))

    filename = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Filename'),
        help_text=_('(.glif xml output filename, autodetected from xml data)'))

    unicode_hex = models.CharField(
        db_index=True,
        max_length=10,
        blank=True,
        default='',
        verbose_name=_('Unicode hex'),
        help_text=_('(unicode hex value, autodetected from xml data)'))

    components = models.TextField(
        blank=True,
        verbose_name=_('Components'))

    @property
    def components_names(self):
        return list(filter(None, self.components.split(',')))

    @property
    def components_cls(self):
        return None

    @property
    def components_set(self):
        return None

    # empty means that there is no deep components instance inside, and no contours and not flat components
    is_empty = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_('Is Empty'),
        help_text=_('(autodetected from xml data)'))

    has_variation_axis = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Has Variation Axis'),
        help_text=_('(autodetected from xml data)'))

    has_outlines = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Has Outlines'),
        help_text=_('(autodetected from xml data)'))

    has_components = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Has Components'),
        help_text=_('(autodetected from xml data)'))

    has_unicode = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Has Unicode'),
        help_text=_('(autodetected from xml data)'))

    def _parse_data(self):
        if self.data:
            gliph_data = GlifData()
            gliph_data.parse_string(self.data)
            if gliph_data.ok:
                return gliph_data
            else:
                logger.error('{} - parse data error: {}'.format(
                    self.__class__, gliph_data.error))
                return None
        return None

    def _apply_data(self, data):
        if data:
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

    def _update_components(self):
        if self.has_components:
            comp_cls = self.components_cls
            if not comp_cls:
                return False
            comp_set = self.components_set
            if not comp_set:
                return False
            comp_names = self.components_names
            # logger.debug(comp_names)
            if comp_names:
                comp_set.clear()
                comp_objs = comp_cls.objects.filter(
                    font_id=self.font_id, name__in=comp_names)
                # logger.debug(comp_objs)
                comp_set.add(*comp_objs)
            else:
                comp_set.clear()
            return True
        return False

    def save(self, *args, **kwargs):
        self._apply_data(self._parse_data())
        super(GlifDataModel, self).save(*args, **kwargs)
        self._update_components()

    def save_to_file_system(self):
        try:
            data_formatted = format_glif(self.data)
        except Exception as formatting_error:
            data_formatted = self.data
            message = 'save_to_file_system glif xml data formatting error - type: {}, id: {}, name: {}, error: {}'.format(
                type(self), self.id, self.name, formatting_error)
            # print(message)
            logger.error(message)
        fsutil.write_file(self.path(), data_formatted)


class CharacterGlyph(GlifDataModel, StatusModel, LockableModel, TimestampModel):

    class Meta:
        app_label = 'robocjk'
        ordering = ['name']
        unique_together = [
            ['font', 'name'],
        ]
        verbose_name = _('Character Glyph')
        verbose_name_plural = _('Character Glyphs')

    font = models.ForeignKey(
        'robocjk.Font',
        on_delete=models.CASCADE,
        related_name='character_glyphs',
        verbose_name=_('Font'))

    deep_components = models.ManyToManyField(
        'robocjk.DeepComponent',
        blank=True,
        related_name='character_glyphs',
        verbose_name=_('Deep Components'))

    objects = CharacterGlyphManager()

    @GlifDataModel.components_cls.getter
    def components_cls(self):
        return DeepComponent

    @GlifDataModel.components_set.getter
    def components_set(self):
        return self.deep_components

    def path(self):
        return get_character_glyph_path(self)

    def serialize(self, **kwargs):
        return serialize_character_glyph(self, **kwargs)

    def __str__(self):
        return force_str('{}'.format(
            self.name))


class CharacterGlyphLayer(GlifDataModel, TimestampModel):

    class Meta:
        app_label = 'robocjk'
        ordering = ['group_name']
        unique_together = [
            ['glif_id', 'group_name', 'name'],
        ]
        verbose_name = _('Character Glyph Layer')
        verbose_name_plural = _('Character Glyph Layers')

    glif = models.ForeignKey(
        'robocjk.CharacterGlyph',
        on_delete=models.CASCADE,
        related_name='layers',
        verbose_name=_('Glif'))

    group_name = models.CharField(
        db_index=True,
        max_length=50,
        verbose_name=_('Group Name'))

    objects = CharacterGlyphLayerManager()

    def path(self):
        return get_character_glyph_layer_path(self)

    def serialize(self, **kwargs):
        return serialize_character_glyph_layer(self, **kwargs)

    def __str__(self):
        return force_str('[{}] {}'.format(
            self.group_name, self.name))


class DeepComponent(GlifDataModel, StatusModel, LockableModel, TimestampModel):

    class Meta:
        app_label = 'robocjk'
        ordering = ['name']
        unique_together = [
            ['font', 'name'],
        ]
        verbose_name = _('Deep Component')
        verbose_name_plural = _('Deep Components')

    font = models.ForeignKey(
        'robocjk.Font',
        on_delete=models.CASCADE,
        related_name='deep_components',
        verbose_name=_('Font'))

    atomic_elements = models.ManyToManyField(
        'robocjk.AtomicElement',
        blank=True,
        related_name='deep_components',
        verbose_name=_('Atomic Elements'))

    objects = DeepComponentManager()

    @GlifDataModel.components_cls.getter
    def components_cls(self):
        return AtomicElement

    @GlifDataModel.components_set.getter
    def components_set(self):
        return self.atomic_elements

    def path(self):
        return get_deep_component_path(self)

    def serialize(self, **kwargs):
        return serialize_deep_component(self, **kwargs)

    def __str__(self):
        return force_str('{}'.format(
            self.name))


class AtomicElement(GlifDataModel, StatusModel, LockableModel, TimestampModel):

    class Meta:
        app_label = 'robocjk'
        ordering = ['name']
        unique_together = [
            ['font', 'name'],
        ]
        verbose_name = _('Atomic Element')
        verbose_name_plural = _('Atomic Elements')

    font = models.ForeignKey(
        'robocjk.Font',
        on_delete=models.CASCADE,
        related_name='atomic_elements',
        verbose_name=_('Font'))

    objects = AtomicElementManager()

    def path(self):
        return get_atomic_element_path(self)

    def serialize(self, **kwargs):
        return serialize_atomic_element(self, **kwargs)

    def __str__(self):
        return force_str('{}'.format(
            self.name))


class AtomicElementLayer(GlifDataModel, TimestampModel):

    class Meta:
        app_label = 'robocjk'
        ordering = ['group_name']
        unique_together = [
            ['glif_id', 'group_name'],
        ]
        verbose_name = _('Atomic Element Layer')
        verbose_name_plural = _('Atomic Element Layers')

    glif = models.ForeignKey(
        'robocjk.AtomicElement',
        on_delete=models.CASCADE,
        related_name='layers',
        verbose_name=_('Glif'))

    group_name = models.CharField(
        db_index=True,
        max_length=50,
        verbose_name=_('Group Name'))

    objects = AtomicElementLayerManager()

    def path(self):
        return get_atomic_element_layer_path(self)

    def serialize(self, **kwargs):
        return serialize_atomic_element_layer(self, **kwargs)

    def __str__(self):
        return force_str('[{}] {}'.format(
            self.group_name, self.name))


class Proof(TimestampModel):

    class Meta:
        app_label = 'robocjk'
        ordering = ['-updated_at']
        verbose_name = _('Proof')
        verbose_name_plural = _('Proofs')

    FILETYPE_PDF = 'pdf'
    FILETYPE_MP4 = 'mp4'
    FILETYPE_CHOICES = (
        (FILETYPE_PDF, _('.pdf'), ),
        (FILETYPE_MP4, _('.mp4'), ),
    )

    font = models.ForeignKey(
        'robocjk.Font',
        on_delete=models.CASCADE,
        related_name='proofs',
        verbose_name=_('Font'))

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name=_('User'))

    filetype = models.CharField(
        max_length=10,
        choices=FILETYPE_CHOICES,
        verbose_name=_('Filetype'))

    file = models.FileField(
        upload_to='proofs',
        validators=[FileExtensionValidator(
            allowed_extensions=('pdf', 'mp4', ))],
        verbose_name=_('File'))

    def path(self):
        return get_proof_path(self)

    def __str__(self):
        return force_str('[{}] {}'.format(
            self.get_filetype_display(), self.file))



from robocjk.signals import *
