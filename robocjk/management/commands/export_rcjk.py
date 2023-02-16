import os
import threading

from django.core.management.base import BaseCommand, CommandError
from extra_settings.models import Setting

from robocjk.debug import logger
from robocjk.models import Project


class Command(BaseCommand):
    help = "Export all .rcjk projects and push changes to their own git repositories."

    def add_arguments(self, parser):
        parser.add_argument(
            "--project-uid",
            required=False,
            help='The uid "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" of the project that will be exported.',
        )
        parser.add_argument(
            "--full",
            action="store_true",
            help="Run full export.",
        )

    def handle(self, *args, **options):
        export_enabled = Setting.get("ROBOCJK_EXPORT_ENABLED", default=True)
        if not export_enabled:
            message = "Export has been disabled through the 'ROBOCJK_EXPORT_ENABLED' setting in the admin."
            self.stderr.write(message)
            raise CommandError(message)

        logger.info("-" * 100)
        logger.info(
            "Start export - pid: {} - thread: {}".format(
                os.getpid(), threading.current_thread().name
            )
        )

        project_uid = options.get("project_uid", None)
        projects_full_export = options.get("full", False)

        if project_uid:
            # export specific project
            try:
                project_obj = Project.objects.get(uid=project_uid)
            except Project.DoesNotExist:
                message = (
                    'Invalid project_uid, project with uid "{}" doesn\'t exist.'.format(
                        project_uid
                    )
                )
                self.stderr.write(message)
                raise CommandError(message)
            else:
                project_obj.export(full=projects_full_export)
        else:
            # export all projects
            projects_qs = Project.objects.prefetch_related("fonts")
            for project in projects_qs:
                project.export(full=projects_full_export)

        logger.info(
            "Complete export - pid: {} - thread: {}".format(
                os.getpid(), threading.current_thread().name
            )
        )
        logger.info("-" * 100)
