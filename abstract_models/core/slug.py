# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from slugify import slugify


class NameSlugModel(models.Model):

    class Meta:
        abstract = True

    name = models.CharField(verbose_name=_('Name'), max_length=50)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=50, unique=True, null=True, blank=True, editable=False)

    def _update_slug(self):
        slug_base = slugify(self.name)
        slug_n = 1
        slug_unique = slug_base
        while self.__class__.objects.exclude(pk=self.pk).filter(slug=slug_unique).exists():
            slug_n += 1
            slug_unique = '{}-{}'.format(slug_base, slug_n)
        self.slug = slug_unique

    def save(self, *args, **kwargs):
        self._update_slug()
        super(NameSlugModel, self).save(*args, **kwargs)


class TitleSlugModel(models.Model):

    class Meta:
        abstract = True

    title = models.CharField(verbose_name=_('Name'), max_length=150)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=150, unique=True, null=True, blank=True, editable=False)

    def _update_slug(self):
        slug_base = slugify(self.name)
        slug_n = 1
        slug_unique = slug_base
        while self.__class__.objects.exclude(pk=self.pk).filter(slug=slug_unique).exists():
            slug_n += 1
            slug_unique = '{}-{}'.format(slug_base, slug_n)
        self.slug = slug_unique

    def save(self, *args, **kwargs):
        self._update_slug()
        super(TitleSlugModel, self).save(*args, **kwargs)

