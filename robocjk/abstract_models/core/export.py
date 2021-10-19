# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import close_old_connections
from django.db import models
from django.utils.translation import ugettext_lazy as _

from robocjk.debug import logger

import datetime as dt


class ExportModel(models.Model):

    class Meta:
        abstract = True

    export_enabled = models.BooleanField(
        default=True,
        verbose_name=_('Export enabled'))

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

    last_full_export_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last full export at'))

    @property
    def full_export_needed(self):
        last_full_export_at = self.last_full_export_at # dt.datetime(year=2021, month=10, day=18, hour=23, minute=59)
        if not last_full_export_at:
            return True
        now = dt.datetime.now()
        last_full_export_older_than_24h = ((now - last_full_export_at) >= dt.timedelta(hours=24))
        last_full_export_day_before = ((now.day - last_full_export_at.day) > 0)
        # print(last_full_export_older_than_24h, last_full_export_day_before)
        return last_full_export_older_than_24h or last_full_export_day_before

    @property
    def export_cancelable(self):
        if self.export_running:
            now = dt.datetime.now()
            if (now - self.export_started_at) > dt.timedelta(minutes=settings.ROBOCJK_EXPORT_CANCEL_TIMEOUT):
                return True
        return False

    @property
    def exportable(self):
        return not self.export_running or self.export_cancelable

    def export(self, full=None):
        close_old_connections()

        cls = self.__class__

        exporting_objects = list(cls.objects.all())
        exportable_objects = [obj.exportable for obj in exporting_objects]
        if not all(exportable_objects):
            logger.warning('Skipped export to avoid overlapping with other exports that are still running.')
            return False

        if not self.export_enabled:
            logger.info('Skipped export for "{}" because it is disabled.'.format(self))
            return False

        if self.export_running:
            if self.export_cancelable:
                logger.warning('Canceled unfinished export for "{}" to allow a new export to start.'.format(self))
                self.export_running = False
                self.save()
            else:
                logger.info('Skipped export for "{}" because there is an export process that is still running.'.format(self))
                return False

        # save export started status in the database
        logger.info('Started export for "{}".'.format(self))
        self.export_running = True
        self.export_started_at = dt.datetime.now()
        self.save()

        # if full argument is provided use it, otherwise use the automated check
        full_export = full if isinstance(full, bool) else self.full_export_needed

        # save model to the file system
        try:
            self.save_to_file_system(full_export)
        except Exception as export_error:
            logger.exception('Canceled export for "{}" due to an unexpected "{}": {}'.format(
                self, type(export_error).__name__, export_error))
            close_old_connections()
            self.export_running = False
            self.save()
            return False

        # save export completed status in the database
        self.export_running = False
        self.export_completed_at = dt.datetime.now()

        if full_export:
            self.last_full_export_at = dt.datetime.now()

        self.save()
        logger.info('Completed export for "{}".'.format(self))
        return True

    def save_to_file_system(self, full_export):
        raise NotImplementedError()

