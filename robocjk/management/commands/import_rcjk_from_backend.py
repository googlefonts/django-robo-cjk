# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from robocjk.models import FontImport

import io


class Command(BaseCommand):

    help = 'Import .rcjk projects uploaded from backend.'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)


    def handle(self, *args, **options):

        if FontImport.objects.filter(status=FontImport.STATUS_LOADING).exists():
            self.stdout.write('There are already one or more fonts being loaded, retry later please.')
            return None

        font_import_objs_qs = FontImport.objects.filter(status=FontImport.STATUS_WAITING)
        font_import_objs = list(font_import_objs_qs)
        if not len(font_import_objs):
            self.stdout.write('There are no fonts (.rcjk) to import.')
            return None

        for font_import_obj in font_import_objs:
            font_import_obj.status = FontImport.STATUS_LOADING
            font_import_obj.save()

        for font_import_obj in font_import_objs:
            font_import_out = io.StringIO()
            font_import_err = io.StringIO()
            try:
                call_command('import_rcjk',
                    filepath=font_import_obj.file.path,
                    font_uid=font_import_obj.font.uid,
                    font_clear=True,
                    stdout=font_import_out,
                    stderr=font_import_err)
            except CommandError:
                pass
            font_import_out_str = font_import_out.getvalue()
            font_import_err_str = font_import_err.getvalue()
            font_import_obj.status = FontImport.STATUS_ERROR if font_import_err_str else FontImport.STATUS_COMPLETED
            font_import_obj.logs = '{}\n---\n{}'.format(
                font_import_out_str, font_import_err_str)
            # print(font_import_obj.logs)
            font_import_obj.save()
