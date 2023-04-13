import os

import fsutil

from robocjk.io.decorators import threaded
from robocjk.io.paths import get_font_path, get_project_path


@threaded
def create_or_update_project(instance, created, **kwargs):
    if created:
        return
    # rename if needed
    if (
        instance.slug
        and instance.initial_slug
        and instance.slug != instance.initial_slug
    ):
        old_name = instance.initial_slug
        old_path = get_project_path(instance, name=old_name)
        if fsutil.exists(old_path):
            new_name = instance.slug
            fsutil.rename_dir(old_path, new_name)


@threaded
def create_or_update_font(instance, created, **kwargs):
    if created:
        return
    # rename if needed
    if (
        instance.slug
        and instance.initial_slug
        and instance.slug != instance.initial_slug
    ):
        old_name = instance.initial_slug
        old_path = get_font_path(instance, name=old_name)
        if fsutil.exists(old_path):
            new_name = os.path.split(get_font_path(instance, name=instance.slug))[-1]
            fsutil.rename_dir(old_path, new_name)


@threaded
def delete_glif(instance, **kwargs):
    instance.delete_from_file_system()
