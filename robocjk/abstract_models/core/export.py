# -*- coding: utf-8 -*-

from django.db import close_old_connections
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
        close_old_connections()
        if self.export_running:
            logger.info('Skipped export for "{}" because there is an export process that is still running.'.format(self))
            now = dt.datetime.now()
            if (now - self.export_started_at) > dt.timedelta(minutes=90):
                logger.warning('Abandoned unfinished export for "{}" to allow a new export to start.'.format(self))
                self.export_running = False
                self.save()
            else:
                return False
        # save export started status in the database
        logger.info('Started export for "{}".'.format(self))
        self.export_running = True
        self.export_started_at = dt.datetime.now()
        self.save()
        # save model to the file system
        try:
            self.save_to_file_system()
        except Exception as export_error:
            logger.error('Canceled export for "{}" due to an unexpected export error: {}'.format(self, export_error))
            close_old_connections()
            self.export_running = False
            self.save()
            return False
        # save export completed status in the database
        self.export_running = False
        self.export_completed_at = dt.datetime.now()
        self.save()
        logger.info('Completed export for "{}".'.format(self))
        return True

    def save_to_file_system(self):
        raise NotImplementedError()

