# -*- coding: utf-8 -*-

from django.core.files.base import ContentFile
from django.core.files import File
from django.db import models

import os
import requests

# TODO: implement logging, install python-fileutil / python-osutil
# from abstract.utils import debug_util, os_util


class FileUtilModel(models.Model):

    class Meta:
        abstract = True

    @staticmethod
    def save_file_content(field, name, content, remove_existing=True):
        # remove existing file to avoid random name suffix
        if field and field.path and os.path.isfile(field.path) and remove_existing:
            os.remove(field.path)
        field.save(name, content=content, save=True)

    @staticmethod
    def save_file_from_path(path, field, name='', remove_existing=True):
        if not os.path.isfile(path):
            msg = 'Invalid path: {}'.format(path)
            # debug_util.log(msg)
            return False
        with open(path, 'rb') as file:
            content = File(file)
            name = name or os_util.get_filename(path)
            self.save_file_content(field, name, content, remove_existing)
        return True

    @staticmethod
    def save_file_from_url(url, field, name='', remove_existing=True, content_types=None):
        if not url or not url.startswith('http'):
            msg = 'Invalid url: {}'.format(url)
            # debug_util.log(msg)
            return False
        try:
            response = requests.get(url, stream=True)
        except Exception as e:
            msg = 'Invalid response (request error): {}'.format(e)
            # debug_util.log(msg)
            return False
        if response.status_code != requests.codes.ok:
            msg = 'Invalid response status code: {}'.format(response.status_code)
            # debug_util.log(msg)
            return False
        content_type = response.headers.get('content-type')
        if content_types and not content_type in content_types:
            msg = 'Invalid response content-type: {}'.format(content_type)
            # debug_util.log(msg)
            return False
        content = ContentFile(response.content)
        name = name or os_util.get_filename(url)
        self.save_file_content(field, name, content, remove_existing)
        return True

    @staticmethod
    def save_image_from_path(path, field, name='', remove_existing=True):
        return self.save_file_from_path(path, field, name, remove_existing)

    @staticmethod
    def save_image_from_url(url, field, name='', remove_existing=True, content_types=None):
        if not content_types:
            content_types = ['image/gif', 'image/jpeg', 'image/jpg', 'image/png']
        return self.save_file_from_url(url, field, name, remove_existing, content_types)

