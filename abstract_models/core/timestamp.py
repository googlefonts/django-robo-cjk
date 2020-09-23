# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class TimestampModel(models.Model):

    class Meta:
        abstract = True

    created_at = models.DateTimeField(verbose_name=_('Created at'), auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True, editable=False)

