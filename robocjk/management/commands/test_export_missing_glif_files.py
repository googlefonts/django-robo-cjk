# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from robocjk.models import CharacterGlyph

import fsutil


class Command(BaseCommand):

    help = 'Test export missing glif files'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        # self.debug_missing_files()
        self.debug_files_saving()

    def debug_files_saving(self):
        print(fsutil.exists("/root/.rcjks/autocjk-hanzi/autocjk-hanzi.rcjk/characterGlyph/uni4F_60.alt00.glif"))
        cg_obj = CharacterGlyph.objects.get(font_id=21, id=458822)
        cg_obj.save_to_file_system()
        print(fsutil.exists(cg_obj.path()))

        print(fsutil.exists("/root/.rcjks/autocjk-hanzi/autocjk-hanzi.rcjk/characterGlyph/uni4F_64.alt00.glif"))
        cg_obj = CharacterGlyph.objects.get(font_id=21, id=458850)
        cg_obj.save_to_file_system()
        print(fsutil.exists(cg_obj.path()))

    def debug_missing_files(self):
        cg_qs = CharacterGlyph.objects.filter(font_id=21).defer("data")
        # print(len(cg_qs))
        for cg_obj in cg_qs:
            cg_path = cg_obj.path()
            if not fsutil.exists(cg_path):
                print(cg_obj.id)
                print(cg_obj)
                print(cg_path)

#         458822
#         uni4F60.alt00
#         /root/.rcjks/autocjk-hanzi/autocjk-hanzi.rcjk/characterGlyph/uni4F_60.alt00.glif
#         -
#         458850
#         uni4F64.alt00
#         /root/.rcjks/autocjk-hanzi/autocjk-hanzi.rcjk/characterGlyph/uni4F_64.alt00.glif