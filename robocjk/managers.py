# -*- coding: utf-8 -*-

from django.db import models


class CharacterGlyphManager(models.Manager):

    def get_queryset(self):
        return super(CharacterGlyphManager, self).get_queryset()


class CharacterGlyphLayerManager(models.Manager):

    def get_queryset(self):
        return super(CharacterGlyphLayerManager, self).get_queryset()


class DeepComponentManager(models.Manager):

    def get_queryset(self):
        return super(DeepComponentManager, self).get_queryset()


class AtomicElementManager(models.Manager):

    def get_queryset(self):
        return super(AtomicElementManager, self).get_queryset()


class AtomicElementLayerManager(models.Manager):

    def get_queryset(self):
        return super(AtomicElementLayerManager, self).get_queryset()
