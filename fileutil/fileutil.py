# -*- coding: utf-8 -*-

# from fileutil.metadata import (
#     __author__, __copyright__, __description__,
#     __license__, __title__, __version__,
# )

from six import PY2
from slugify import slugify

try:
    # python 2
    from urlparse import urlsplit
except ImportError:
    # python 3
    from urllib.parse import urlsplit

import errno
import hashlib
import os
import shutil
import uuid


def assert_dir(path):
    """
    Raise an OSError if the given path doesn't exist or it is not a directory.
    """
    if not is_dir(path):
        raise OSError('Invalid directory path: {}'.format(path))


def assert_exists(path):
    """
    Raise an OSError if the given path doesn't exist.
    """
    if not exists(path):
        raise OSError('Invalid item path: {}'.format(path))


def assert_file(path):
    """
    Raise an OSError if the given path doesn't exist or it is not a file.
    """
    if not is_file(path):
        raise OSError('Invalid file path: {}'.format(path))


def assert_not_dir(path):
    """
    Raise an OSError if the given path is an existing directory.
    """
    if is_dir(path):
        raise OSError('Invalid path, directory already exists: {}'.format(path))


def assert_not_file(path):
    """
    Raise an OSError if the given path is an existing file.
    """
    if is_file(path):
        raise OSError('Invalid path, file already exists: {}'.format(path))


def assert_not_exists(path):
    """
    Raise an OSError if the given path already exists.
    """
    if exists(path):
        raise OSError('Invalid path, item already exists: {}'.format(path))


# def copy_dir(path, dest, overwrite=False):
#     assert_dir(path)
#     if not overwrite:
#         assert_not_exists(dest)
#     # TODO
#     pass
#
#
# def copy_file(path, dest, overwrite=False):
#     assert_file(path)
#     if not overwrite:
#         assert_not_exists(dest)
#     # TODO
#     pass


def create_dir(path, overwrite=False):
    if not overwrite:
        assert_not_exists(path)
    # TODO
    pass


def create_file(path, overwrite=False, content=''):
    if not overwrite:
        assert_not_exists(path)
    # TODO
    pass


# def create_temp_dir():
#     # TODO
#     pass
#
#
# def create_temp_file():
#     # TODO
#     pass


def delete_dir(path):
    return remove_dir(path)


def delete_dirs(*paths):
    remove_dirs(*paths)


def delete_empty_dirs(path):
    remove_empty_dirs(path)


def delete_file(path):
    return remove_file(path)


def delete_files(*paths):
    remove_files(*paths)


def ensure_dirpath(path):
    if is_dir(path):
        return
    assert_not_file(path)
    try:
        os.makedirs(path)
    except OSError as e:
        # Guard against race condition
        if e.errno != errno.EEXIST:
            raise e


def ensure_filepath(path):
    dirpath, filename = split_filepath(path)
    ensure_dirpath(dirpath)


def exists(path):
    return os.path.exists(path)


def get_basename(path):
    basename, _ = split_filename(path)
    return basename


def get_extension(path):
    _, extension = split_filename(path)
    return extension


def get_filename(path):
    filepath = urlsplit(path).path
    filename = os.path.basename(filepath)
    return filename


def get_hash(path, func='md5'):
    # hash = hashlib.md5()
    hash = hashlib.new(func)
    paths = list(path) if isinstance(path, (list, set, tuple, )) else [path]
    paths.sort()
    for path in paths:
        with open(path, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b''):
                hash.update(chunk)
    hash_hex = hash.hexdigest()
    return hash_hex


def get_size(path):
    return os.path.getsize(path)


# def get_size_formatted(path):
#     # TODO:
#     pass


def get_unique_name():
    name = uuid.uuid4()
    name = name.replace('-', '')
    return name


def is_dir(path):
    """
    Determines whether the specified path represents an existing directory.

    :param path: The path
    :type path: { str }

    :returns: True if the specified path is dir, False otherwise.
    :rtype: boolean
    """
    return os.path.isdir(path)


def is_empty(path):
    """
    Determines whether the specified path is an empty directory.

    :param path: The path
    :type path: { bool }

    :returns: True if the specified path is empty, False otherwise.
    :rtype: boolean
    """
    if is_dir(path):
        return len(list_files(path)) == 0
    return False


def is_file(path):
    """
    Determines whether the specified path represents an existing file.

    :param path: The path
    :type path: { str }

    :returns: True if the specified path is file, False otherwise.
    :rtype: boolean
    """
    return os.path.isfile(path)


def join_filename(basename, extension):
    basename = basename.rstrip('.').strip()
    extension = extension.replace('.', '').strip()
    filename = '{}.{}'.format(basename, extension)
    return filename


def join_filepath(dirpath, filename):
    filepath = os.path.join(dirpath, filename)
    return filepath


# def list_dir(path, dirs=True, files=True):
#     assert_dir(path)
#     if not dirs and not files:
#         return []
#     items = os.listdir(path)
#     if not dirs:
#         items = [item for item in items if not is_dir(item)]
#     if not files:
#         items = [item for item in items if not is_file(item)]
#     return items
#
#
# def move_dir(path, dest, overwrite=False):
#     assert_dir(path)
#     if not overwrite:
#         assert_not_exists(dest)
#     # TODO
#     pass
#
#
# def move_file(path, dest, overwrite=False):
#     assert_file(path)
#     if not overwrite:
#         assert_not_exists(dest)
#     # TODO
#     pass


# def norm_filename(path):
#     basename, extension = split_filename(path)
#     basename = slugify(basename)
#     filename = join_filename(basename, extension)
#     return filename


def read_file(path):
    # TODO
    pass


# def read_file_lines(path, blank=False):
#     # TODO
#     pass


def rename_dir(path, name, overwrite=False):
    assert_dir(path)
    comps = list(os.path.split(path))
    comps[-1] = name
    dest = os.path.join(*comps)
    if not overwrite:
        assert_not_exists(dest)
    # shutil.move(path, dest)
    os.rename(path, dest)


def rename_file(path, name, overwrite=False):
    assert_file(path)
    dirpath, filename = split_filepath(path)
    dest = join_filepath(dirpath, name)
    if not overwrite:
        assert_not_exists(dest)
    # shutil.move(path, dest)
    os.rename(path, dest)


# def rename_file_extension(path, extension):
#     basename, ext = split_filename(path)
#     name = join_filename(basename, extension)
#     rename_file(path, name)


def remove_dir(path):
    if is_dir(path):
        shutil.rmtree(path, ignore_errors=True)
        return True
    return False


def remove_dirs(*paths):
    for path in paths:
        remove_dir(path)


def remove_empty_dirs(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in dirs:
            dirpath = os.path.join(root, dir)
            if is_empty(dirpath):
                # print(dirpath)
                # delete_dir(dirpath)
                os.rmdir(dirpath)


def remove_file(path):
    if is_file(path):
        os.remove(path)
        return True
    return False


def remove_files(*paths):
    for path in paths:
        remove_file(path)


# def search_files(path, prefix='', suffix='', traverse=False):
#     assert_dir(path)
#     # results = []
#     def find_files_in(files):
#         for filename in files:
#             if prefix and not filename.startswith(prefix):
#                 continue
#             if suffix and not filename.endswith(suffix):
#                 continue
#             filepath = os.path.join(path, filename)
#             yield filepath
#     if traverse:
#         for root, dirs, files in os.walk(path):
#             find_files_in(files)
#     else:
#         files = os.listdir(path)
#         find_files_in(files)
#     return results


def split_filename(path):
    filename = get_filename(path)
    basename, extension = os.path.splitext(filename)
    extension = extension.replace('.', '').strip()
    return (basename, extension, )


def split_filepath(path):
    dirpath = os.path.dirname(path)
    filename = get_filename(path)
    return (dirpath, filename, )


# https://www.simplifiedpython.net/python-zip-file-example/


# def zip_file_open(path, dest='.', autodelete=False):
#     # TODO
#     pass


def write_file_dir(filepath):
    ensure_dirpath(filepath)


def write_file(filepath, content, encoding='utf-8'):
    # https://stackoverflow.com/questions/12517451/automatically-creating-directories-with-file-output
    ensure_filepath(filepath)
    options = {} if PY2 else { 'encoding':encoding }
    with open(filepath, 'w', **options) as file:
        file.write(content)
    return True


# def write_zip_file(path, src, compression=zipfile.ZIP_DEFLATED):
#     # TODO
#     pass

# create
# read
# extract_file
# extract_all

# from django.core.files import File


# def save_file_to_django_field(filepath, field):
#     with open(filepath, 'rb') as file:
#         filename = file_util.get_filename(filepath)
#         # filename = slugify(filename) + file extension lower
#         print(filename)
#         file_obj = File(file)
#         field.save(filename, file_obj, save=True)

