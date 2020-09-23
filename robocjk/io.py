# -*- coding: utf-8 -*-

from fileutil import fileutil

import os


def sync_project(instance):
    # if created:
     # fileutil.write_file_dir(instance.project_path)
    # return
    # import subprocess
    path = instance.get_absolute_path()
    cmds = []
    cmds.append('mkdir -p {}'.format(path))
    cmds.append('cd {}'.format(path))
    cmds.append('git init')
    # cmds.append('git remote add origin {}'.format(instance.repo_url))
    # cmds.append('git pull origin master')
    cmd = ' && '.join(cmds)
    os.system(cmd)
    # status = subprocess.call(cmd, shell=True)


def delete_project(instance):
    pass


def sync_font(instance):
    path = instance.get_absolute_path()
    cmds = []
    cmds.append('mkdir -p {}'.format(path))
    cmds.append('cd {}'.format(path))
    cmd = ' && '.join(cmds)
    os.system(cmd)


def delete_font(instance):
    pass


def sync_character_glyph(instance):
    path = instance.get_absolute_path()
    fileutil.write_file(path, instance.data)


def delete_character_glyph(instance):
    path = instance.get_absolute_path()
    fileutil.delete_file(path)


def sync_character_glyph_layer(instance):
    path = instance.get_absolute_path()
    fileutil.write_file(path, instance.data)


def delete_character_glyph_layer(instance):
    path = instance.get_absolute_path()
    fileutil.delete_file(path)


def sync_deep_component(instance):
    path = instance.get_absolute_path()
    fileutil.write_file(path, instance.data)


def delete_deep_component(instance):
    path = instance.get_absolute_path()
    fileutil.delete_file(path)


def sync_atomic_element(instance):
    path = instance.get_absolute_path()
    fileutil.write_file(path, instance.data)


def delete_atomic_element(instance):
    path = instance.get_absolute_path()
    fileutil.delete_file(path)


def sync_atomic_element_layer(instance):
    path = instance.get_absolute_path()
    fileutil.write_file(path, instance.data)


def delete_atomic_element_layer(instance):
    path = instance.get_absolute_path()
    fileutil.delete_file(path)

