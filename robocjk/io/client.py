# from robocjk.debug import logger
import os

import fsutil

from robocjk.io.decorators import threaded
from robocjk.io.paths import (  # get_character_glyph_path,; get_character_glyph_layer_path,; get_deep_component_path,; get_atomic_element_path,; get_atomic_element_layer_path,; get_proof_path,
    get_font_path,
    get_project_path,
)


def run_system_commands(*args):
    cmd = " && ".join(args)
    os.system(cmd)


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
    # init git repository if needed


#     path = instance.path()
#     fsutil.ensure_dirpath(path)
#     git_repo_path = os.path.join(path, '.git')
#     if not fsutil.exists(git_repo_path):
#         run_system_commands(
#             'cd {}'.format(path),
#             'git init',
#             'git remote add origin {}'.format(instance.repo_url),
#             'git pull origin main'
#         )


# @threaded
# def delete_project(instance, **kwargs):
#     fsutil.delete_dir(instance.path())


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
    # fsutil.ensure_dirpath(instance.path())


# @threaded
# def delete_font(instance, **kwargs):
#     fsutil.delete_dir(instance.path())
#
#
# @threaded
# def create_or_update_character_glyph(instance, created, **kwargs):
# #     if not created:
# #         # rename if needed
# #         if instance.filename and instance.initial_filename and instance.filename != instance.initial_filename:
# #             old_filename = instance.initial_filename
# #             old_filepath = get_character_glyph_path(instance, filename=old_filename)
# #             if fsutil.exists(old_filepath):
# #                 new_filepath = os.path.split(get_character_glyph_path(instance, filename=instance.filename))[-1]
# #                 fsutil.rename_file(old_filepath, name=new_filepath)
#     fsutil.write_file(instance.path(), instance.data)


@threaded
def delete_character_glyph(instance, **kwargs):
    fsutil.delete_file(instance.path())


# @threaded
# def create_or_update_character_glyph_layer(instance, created, **kwargs):
#     fsutil.write_file(instance.path(), instance.data)


@threaded
def delete_character_glyph_layer(instance, **kwargs):
    fsutil.delete_file(instance.path())


# @threaded
# def create_or_update_deep_component(instance, created, **kwargs):
#     fsutil.write_file(instance.path(), instance.data)


@threaded
def delete_deep_component(instance, **kwargs):
    fsutil.delete_file(instance.path())


# @threaded
# def create_or_update_atomic_element(instance, created, **kwargs):
#     fsutil.write_file(instance.path(), instance.data)


@threaded
def delete_atomic_element(instance, **kwargs):
    fsutil.delete_file(instance.path())


# @threaded
# def create_or_update_atomic_element_layer(instance, created, **kwargs):
#     fsutil.write_file(instance.path(), instance.data)


@threaded
def delete_atomic_element_layer(instance, **kwargs):
    fsutil.delete_file(instance.path())


# @threaded
# def create_or_update_proof(instance, created, **kwargs):
#     fsutil.write_file(instance.path(), instance.data)
#
#
# @threaded
# def delete_proof(instance, **kwargs):
#     fsutil.delete_file(instance.path())
