# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from robocjk.debug import logger
from robocjk.models import Project

import os
import threading


class Command(BaseCommand):

    help = 'Export all .rcjk projects and push changes to their own git repositories.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Run full export.',
        )

    def handle(self, *args, **options):

        logger.info('-' * 100)
        logger.info('Start export - pid: {} - thread: {}'.format(
            os.getpid(), threading.current_thread().name))

        projects_full_export = options.get('full', False)
        projects_qs = Project.objects.prefetch_related('fonts')
        for project in projects_qs:
            project.export(full=projects_full_export)

        logger.info('Complete export - pid: {} - thread: {}'.format(
            os.getpid(), threading.current_thread().name))
        logger.info('-' * 100)
