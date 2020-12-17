# -*- coding: utf-8 -*-

from django.db import models


class ProjectManager(models.Manager):

    def get_queryset(self):
        qs = super(ProjectManager, self).get_queryset()
        # qs = qs.prefetch_related('fonts')
        return qs


class FontManager(models.Manager):

    def get_queryset(self):
        qs = super(FontManager, self).get_queryset()
        # qs = qs.select_related('project')
        # qs = qs.prefetch_related('atomic_elements', 'deep_components', 'character_glyphs')
        return qs


class CharacterGlyphManager(models.Manager):

    def get_queryset(self):
        qs = super(CharacterGlyphManager, self).get_queryset()
        # qs = qs.select_related('font')
        # qs = qs.prefetch_related('layers')
        return qs


class CharacterGlyphLayerManager(models.Manager):

    def get_queryset(self):
        qs = super(CharacterGlyphLayerManager, self).get_queryset()
        # qs = qs.select_related('glif')
        return qs


class DeepComponentManager(models.Manager):

    def get_queryset(self):
        qs = super(DeepComponentManager, self).get_queryset()
        # qs = qs.select_related('font')
        return qs


class AtomicElementManager(models.Manager):

    def get_queryset(self):
        qs = super(AtomicElementManager, self).get_queryset()
        # qs = qs.select_related('font')
        # qs = qs.prefetch_related('layers')
        return qs


class AtomicElementLayerManager(models.Manager):

    def get_queryset(self):
        qs = super(AtomicElementLayerManager, self).get_queryset()
        # qs = qs.select_related('glif')
        return qs

