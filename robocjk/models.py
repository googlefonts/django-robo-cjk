# -*- coding: utf-8 -*-

from abstract_models import (
    UIDModel, HashidModel, NameSlugModel, TimestampModel, )

from benedict import benedict
from benedict.serializers import Base64Serializer

from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.signals import (post_save, pre_delete, )
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str

from fileutil import fileutil

from . import io
from .api.serializers import (
    serialize_atomic_element,
    serialize_atomic_element_layer,
    serialize_deep_component,
    serialize_character_glyph,
    serialize_character_glyph_layer,
)
from .core import GlifData
from .debug import logger
from .managers import (
    CharacterGlyphManager, CharacterGlyphLayerManager,
    DeepComponentManager,
    AtomicElementManager, AtomicElementLayerManager, )

import datetime as dt
import os


"""
1. “atomic elements” contain only outlines, not references to other atomic elements
2. “deep components” contain only references to atomic elements, and do not contain outlines
3. “character glyphs”, contain only references to deep components, not to atomic elements, and outlines
"""


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
        max_length=200,
        verbose_name=_('Repo URL'),
        help_text=_('The .git repository URL'))

    def get_absolute_path(self):
        return '/root/robocjk-projects/{}'.format(
            self.slug)

    @staticmethod
    def post_save_handler(instance, created, **kwargs):
        # if created:
        io.sync_project(instance)

    @staticmethod
    def pre_delete_handler(instance, using, **kwargs):
        io.delete_project(instance)

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

    def get_absolute_path(self):
        return '{}/{}.rcjk'.format(
            self.project.get_absolute_path(), self.slug)

    @staticmethod
    def post_save_handler(instance, created, **kwargs):
        # if created:
        io.sync_font(instance)

    @staticmethod
    def pre_delete_handler(instance, using, **kwargs):
        io.delete_font(instance)

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

    def _lock_by(self, user):
        self.is_locked = True
        self.locked_by = user
        self.locked_at = dt.datetime.now()
        self.save()

    def _unlock_by(self, user):
        self.is_locked = False
        self.locked_by = None
        self.locked_at = None
        self.save()

    def lock_by(self, user):
        if not self._is_valid_user(user):
            return False
        if not self.is_locked:
            self._lock_by(user)
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

    def unlock_by(self, user):
        if not self._is_valid_user(user):
            return False
        if self.is_locked:
            if self.locked_by_id == user.id:
                self._unlock_by(user)
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
    STATUS_COLORS = {
        STATUS_TODO: '#E74C3C',
        STATUS_WIP: '#E67E22',
        STATUS_CHECKING_1: '#F1C40F',
        STATUS_CHECKING_2: '#F1C40F',
        STATUS_CHECKING_3: '#F1C40F',
        STATUS_DONE: '#2ECC71',
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

    def get_absolute_path(self):
        return '{}/characterGlyph/{}'.format(
            self.font.get_absolute_path(), self.filename)

    def serialize(self, **kwargs):
        return serialize_character_glyph(self, *kwargs)

    @staticmethod
    def post_save_handler(instance, created, **kwargs):
        io.sync_character_glyph(instance)

    @staticmethod
    def pre_delete_handler(instance, using, **kwargs):
        io.delete_character_glyph(instance)

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

    def get_absolute_path(self):
        return '{}/characterGlyph/{}/{}'.format(
            self.glif.font.get_absolute_path(), self.group_name, self.filename)

    def serialize(self, **kwargs):
        return serialize_character_glyph_layer(self, **kwargs)

    @staticmethod
    def post_save_handler(instance, created, **kwargs):
        io.sync_character_glyph_layer(instance)

    @staticmethod
    def pre_delete_handler(instance, using, **kwargs):
        io.delete_character_glyph_layer(instance)

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

    def get_absolute_path(self):
        return '{}/deepComponent/{}'.format(
            self.font.get_absolute_path(), self.filename)

    def serialize(self, **kwargs):
        return serialize_deep_component(self, **kwargs)

    @staticmethod
    def post_save_handler(instance, created, **kwargs):
        io.sync_deep_component(instance)

    @staticmethod
    def pre_delete_handler(instance, using, **kwargs):
        io.delete_deep_component(instance)

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

    def get_absolute_path(self):
        return '{}/atomicElement/{}'.format(
            self.font.get_absolute_path(), self.filename)

    def serialize(self, **kwargs):
        return serialize_atomic_element(self, **kwargs)

    @staticmethod
    def post_save_handler(instance, created, **kwargs):
        io.sync_atomic_element(instance)

    @staticmethod
    def pre_delete_handler(instance, using, **kwargs):
        io.delete_atomic_element(instance)

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

    def get_absolute_path(self):
        return '{}/atomicElement/{}/{}'.format(
            self.glif.font.get_absolute_path(), self.group_name, self.filename)

    def serialize(self, **kwargs):
        return serialize_atomic_element_layer(self, **kwargs)

    @staticmethod
    def post_save_handler(instance, created, **kwargs):
        io.sync_atomic_element_layer(instance)

    @staticmethod
    def pre_delete_handler(instance, using, **kwargs):
        io.delete_atomic_element_layer(instance)

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

    user = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('User'))

    filetype = models.CharField(
        max_length=10,
        choices=FILETYPE_CHOICES,
        verbose_name=_('Filetype'))

    file = models.FileField(
        upload_to='proofs',
        validators=[FileExtensionValidator(
            allowed_extensions=('pdf', 'mp4', ))],
        verbose_name=_('Proofs'))

    # def get_absolute_path(self):
    #     return 'Proofing/{}/{}'.format(
    #         self.glif.font.get_absolute_path(), self.group_name, self.filepath)

    # @staticmethod
    # def post_save_handler(instance, created, **kwargs):
    #     pass

    # @staticmethod
    # def pre_delete_handler(instance, using, **kwargs):
    #     pass

    def __str__(self):
        return force_str('[{}] {}'.format(
            self.get_filetype_display(), self.file))


post_save.connect(Font.post_save_handler, sender=Font)
pre_delete.connect(Font.pre_delete_handler, sender=Font)

post_save.connect(CharacterGlyph.post_save_handler, sender=CharacterGlyph)
pre_delete.connect(CharacterGlyph.pre_delete_handler, sender=CharacterGlyph)

post_save.connect(CharacterGlyphLayer.post_save_handler, sender=CharacterGlyphLayer)
pre_delete.connect(CharacterGlyphLayer.pre_delete_handler, sender=CharacterGlyphLayer)

post_save.connect(DeepComponent.post_save_handler, sender=DeepComponent)
pre_delete.connect(DeepComponent.pre_delete_handler, sender=DeepComponent)

post_save.connect(AtomicElement.post_save_handler, sender=AtomicElement)
pre_delete.connect(AtomicElement.pre_delete_handler, sender=AtomicElement)

post_save.connect(AtomicElementLayer.post_save_handler, sender=AtomicElementLayer)
pre_delete.connect(AtomicElementLayer.pre_delete_handler, sender=AtomicElementLayer)

# pre_delete.connect(Proof.pre_delete_handler, sender=Proof)
# post_save.connect(Proof.post_save_handler, sender=Proof)

