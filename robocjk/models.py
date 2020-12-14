# -*- coding: utf-8 -*-

from benedict import benedict
from benedict.serializers import Base64Serializer

from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str

from robocjk.abstract_models import (
    UIDModel, HashidModel, NameSlugModel, TimestampModel,
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
    get_character_glyph_path,
    get_character_glyph_layer_path,
    get_deep_component_path,
    get_atomic_element_path,
    get_atomic_element_layer_path,
    get_proof_path,
)
from robocjk.managers import (
    CharacterGlyphManager, CharacterGlyphLayerManager,
    DeepComponentManager,
    AtomicElementManager, AtomicElementLayerManager,
)
from robocjk.settings import GIT_SSH_REPOSITORY_URL_VALIDATOR

import datetime as dt
import fsutil
import os


"""
1. “atomic elements” contain only outlines, not references to other atomic elements
2. “deep components” contain only references to atomic elements, and do not contain outlines
3. “character glyphs”, contain only references to deep components, not to atomic elements, and outlines
"""

repo_ssh_url_validator = GIT_SSH_REPOSITORY_URL_VALIDATOR


class Project(UIDModel, HashidModel, NameSlugModel, TimestampModel):
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
        validators=[repo_ssh_url_validator],
        verbose_name=_('Repo URL'),
        help_text=_('The .git repository SSH URL, eg. git@github.com:username/repository.git'))

    def num_fonts(self):
        return self.fonts.count()

    def path(self):
        return get_project_path(self)

    def save_by(self, user):
        self.updated_by = user
        self.save()

    def save_to_file_system(self):
        path = self.path()
        fsutil.remove_dir(path)
        fsutil.make_dirs(path)
        # init git repository if needed
        git_repo_path = fsutil.join_path(path, '.git')
        if not fsutil.exists(git_repo_path):
            cmds = [
                'cd {}'.format(path),
                'git init',
                'git remote add origin {}'.format(self.repo_url),
                'git pull origin master',
            ]
            cmd = ' && '.join(cmds)
            os.system(cmd)
        # save all project fonts to file.system
        fonts_qs = self.fonts.prefetch_related(
            'character_glyphs',
            'character_glyphs__layers',
            'deep_components',
            'atomic_elements',
            'atomic_elements__layers').filter(available=True)
        for font in fonts_qs:
            font.save_to_file_system()
            cmds = [
                'cd {}'.format(path),
                'git add -A',
                'git commit -m "{}"'.format(
                    'Updated {}.'.format(font.name)),
                'git push -u origin master',
            ]
            cmd = ' && '.join(cmds)
            os.system(cmd)

    def serialize(self, **kwargs):
        return serialize_project(self, *kwargs)

    def __str__(self):
        return force_str('{}'.format(
            self.name))


class Font(UIDModel, HashidModel, NameSlugModel, TimestampModel):
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

    glyphs_composition = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        verbose_name=_('Glyphs Composition'))

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

    def save_by(self, user):
        self.updated_by = user
        self.save()

    def save_to_file_system(self):
        path = self.path()
        fsutil.make_dirs(path)
        # write fontlib.json file
        fontlib_path = fsutil.join_path(path, 'fontLib.json')
        fontlib_str = benedict(self.fontlib, keypath_separator=None).dump()
        fsutil.write_file(fontlib_path, fontlib_str)
        # write all character-glyphs and relative layers
        for character_glyph in self.character_glyphs.all():
            character_glyph.save_to_file_system()
        # write all deep-components
        for deep_component in self.deep_components.all():
            deep_component.save_to_file_system()
        # write all atomic-elements and relative layers
        for atomic_element in self.atomic_elements.all():
            atomic_element.save_to_file_system()

    def serialize(self, **kwargs):
        return serialize_font(self, *kwargs)

    def __str__(self):
        return force_str('{}'.format(
            self.name))


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
        return self.locked_by == user

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

    STATUS_TODO = 'todo'
    STATUS_WIP = 'wip'
    STATUS_CHECKING_1 = 'checking-1'
    STATUS_CHECKING_2 = 'checking-2'
    STATUS_CHECKING_3 = 'checking-3'
    STATUS_DONE = 'done'
    STATUS_CHOICES = (
        (STATUS_TODO, _('Todo'), ),
        (STATUS_WIP, _('Wip'), ),
        (STATUS_CHECKING_1, _('Checking 1'), ),
        (STATUS_CHECKING_2, _('Checking 2'), ),
        (STATUS_CHECKING_3, _('Checking 3'), ),
        (STATUS_DONE, _('Done'), ),
    )
    STATUS_CHOICES_VALUES_LIST = [
        STATUS_TODO,
        STATUS_WIP,
        STATUS_CHECKING_1,
        STATUS_CHECKING_2,
        STATUS_CHECKING_3,
        STATUS_DONE,
    ]
    STATUS_COLORS = {
        STATUS_TODO: '#999999', # grey
        STATUS_WIP: '#e74c3c', # '#FF0000', # red
        STATUS_CHECKING_1: '#e67e22', # '#FF8800', # orange
        STATUS_CHECKING_2: '#f1c40f', # '#FFFF00', # yellow
        STATUS_CHECKING_3: '#2980b9', # '#0088FF', # blue
        STATUS_DONE: '#27ae60', # '#00FF88', # green
    }
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_TODO,
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
                logger.debug('{} - parse data error: {}'.format(
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

    def save_by(self, user):
        self.updated_by = user
        self.save()

    def save_to_file_system(self):
        fsutil.write_file(self.path(), self.data)


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

    def save_to_file_system(self):
        super(CharacterGlyph, self).save_to_file_system()
        for layer in self.layers.all():
            layer.save_to_file_system()

    def serialize(self, **kwargs):
        return serialize_character_glyph(self, *kwargs)

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

    def save_to_file_system(self):
        super(AtomicElement, self).save_to_file_system()
        for layer in self.layers.all():
            layer.save_to_file_system()

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
