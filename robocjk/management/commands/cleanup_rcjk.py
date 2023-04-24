import os
import threading

from django.core.management.base import BaseCommand, CommandError

from robocjk.debug import logger
from robocjk.models import Project


class Command(BaseCommand):
    help = "Cleanup .rcjk projects by removing zombie files from file-system."

    def add_arguments(self, parser):
        parser.add_argument(
            "--project-uid",
            required=False,
            help="The uid 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx' of the project that will be cleaned up.",
        )
        parser.add_argument(
            "--all-projects",
            action="store_true",
            help="Cleanup all projects.",
        )

    def handle(self, *args, **options):
        process_id = os.getpid()
        thread_name = threading.current_thread().name
        logger.info(f"Start cleanup - pid: {process_id} - thread: {thread_name}")

        project_uid = options.get("project_uid", None)
        all_projects = options.get("all_projects", False)

        if project_uid:
            # export specific project
            try:
                project_obj = Project.objects.get(uid=project_uid)
                project_obj.cleanup_file_system()
            except Project.DoesNotExist:
                message = f"Invalid project_uid, project with uid {project_uid!r} doesn't exist."
                self.stderr.write(message)
                raise CommandError(message)
        elif all_projects:
            # export all projects
            projects_qs = Project.objects.prefetch_related("fonts")
            for project_obj in projects_qs:
                project_obj.cleanup_file_system()
        else:
            message = "Missing expected argument --project-uid or --all-projects"
            raise CommandError(message)

        process_id = os.getpid()
        thread_name = threading.current_thread().name
        logger.info(f"Complete cleanup - pid: {process_id} - thread: {thread_name}")

        logger.info("-" * 100)
