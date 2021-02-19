# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from robocjk.debug import logger

import datetime as dt


class ExportModel(models.Model):

    class Meta:
        abstract = True

    export_running = models.BooleanField(
        default=False,
        verbose_name=_('Export running'))

    export_started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Export started at'))

    export_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Export completed at'))

    def export(self):
        if self.export_running:
            logger.error('Skipped export because there is an export process that is still running.')
            return False
        # save export started status in the database
        self.export_running = True
        self.export_started_at = dt.datetime.now()
        self.save()
        # save model to the file system
        self.save_to_file_system()
        # save export completed status in the database
        self.export_running = False
        self.export_completed_at = dt.datetime.now()
        self.save()
        return True

    def save_to_file_system(self):
        raise NotImplementedError()

