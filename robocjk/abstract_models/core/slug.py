from django.db import models
from django.utils.translation import gettext_lazy as _
from slugify import slugify


class NameSlugModel(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=50,
    )
    slug = models.SlugField(
        verbose_name=_("Slug"),
        max_length=50,
        # unique=True,
        db_index=True,
        null=True,
        blank=True,
        editable=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_name = self.name
        self.initial_slug = self.slug

    def _update_slug(self):
        self.slug = slugify(self.name)

    #         slug_base = slugify(self.name)
    #         slug_n = 1
    #         slug_unique = slug_base
    #         while (
    #             self.__class__.objects.exclude(pk=self.pk).filter(slug=slug_unique).exists()
    #         ):
    #             slug_n += 1
    #             slug_unique = f"{slug_base}-{slug_n}"
    #         self.slug = slug_unique

    def save(self, *args, **kwargs):
        self._update_slug()
        super().save(*args, **kwargs)
        self.initial_name = self.name
        self.initial_slug = self.slug


class TitleSlugModel(models.Model):
    class Meta:
        abstract = True

    title = models.CharField(
        verbose_name=_("Name"),
        max_length=150,
    )
    slug = models.SlugField(
        verbose_name=_("Slug"),
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        editable=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_title = self.title
        self.initial_slug = self.slug

    def _update_slug(self):
        slug_base = slugify(self.name)
        slug_n = 1
        slug_unique = slug_base
        while (
            self.__class__.objects.exclude(pk=self.pk).filter(slug=slug_unique).exists()
        ):
            slug_n += 1
            slug_unique = f"{slug_base}-{slug_n}"
        self.slug = slug_unique

    def save(self, *args, **kwargs):
        self._update_slug()
        super().save(*args, **kwargs)
        self.initial_title = self.title
        self.initial_slug = self.slug
