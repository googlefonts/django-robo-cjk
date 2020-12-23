# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _


class TimestampModel(models.Model):

    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_('Created at'))

    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name=_('Updated at'))

    updated_by = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Updated by'))

    def save_by(self, user):
        self.updated_by = user
        self.save()
