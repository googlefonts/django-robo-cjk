import fsutil
from django.core.management.base import BaseCommand

from robocjk.models import CharacterGlyph, CharacterGlyphLayer


class Command(BaseCommand):
    help = "Test export missing glif files"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):
        # self.debug_missing_character_glyphs_files()
        # self.debug_missing_character_glyphs_layers_files()
        self.debug_character_glyphs_files_saving()
        self.debug_character_glyphs_layers_files_saving()
        pass

    def debug_character_glyphs_files_saving(self):
        for cg_id in [458822, 458850]:
            cg_obj = CharacterGlyph.objects.get(font_id=21, id=cg_id)
            print(cg_obj, fsutil.exists(cg_obj.path()))
            cg_obj.save_to_file_system()
            print(cg_obj, fsutil.exists(cg_obj.path()))
            print("---")

    def debug_character_glyphs_layers_files_saving(self):
        for cg_layer_id in [723047, 723048, 723049, 723050, 723101, 723102]:
            cg_layer_obj = CharacterGlyphLayer.objects.get(
                glif__font_id=21, id=cg_layer_id
            )
            print(cg_layer_obj, fsutil.exists(cg_layer_obj.path()))
            cg_layer_obj.save_to_file_system()
            print(cg_layer_obj, fsutil.exists(cg_layer_obj.path()))
            print("---")

    def debug_missing_character_glyphs_files(self):
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

    #         458850
    #         uni4F64.alt00
    #         /root/.rcjks/autocjk-hanzi/autocjk-hanzi.rcjk/characterGlyph/uni4F_64.alt00.glif

    def debug_missing_character_glyphs_layers_files(self):
        cg_layers_qs = CharacterGlyphLayer.objects.filter(glif__font_id=21).defer(
            "data"
        )
        # print(len(cg_layers_qs))
        for cg_layer_obj in cg_layers_qs:
            cg_layer_path = cg_layer_obj.path()
            if not fsutil.exists(cg_layer_path):
                print(cg_layer_obj.id)
                print(cg_layer_obj)
                print(cg_layer_path)


#         723047
#         [backup_master] uni4F60.alt00
#         /root/.rcjks/autocjk-hanzi/autocjk-hanzi.rcjk/characterGlyph/backup_master/uni4F_60.alt00.glif

#         723048
#         [backup_wght] uni4F60.alt00
#         /root/.rcjks/autocjk-hanzi/autocjk-hanzi.rcjk/characterGlyph/backup_wght/uni4F_60.alt00.glif

#         723049
#         [bold] uni4F60.alt00
#         /root/.rcjks/autocjk-hanzi/autocjk-hanzi.rcjk/characterGlyph/bold/uni4F_60.alt00.glif

#         723050
#         [wght] uni4F60.alt00
#         /root/.rcjks/autocjk-hanzi/autocjk-hanzi.rcjk/characterGlyph/wght/uni4F_60.alt00.glif

#         723101
#         [backup_master] uni4F64.alt00
#         /root/.rcjks/autocjk-hanzi/autocjk-hanzi.rcjk/characterGlyph/backup_master/uni4F_64.alt00.glif

#         723102
#         [backup_wght] uni4F64.alt00
#         /root/.rcjks/autocjk-hanzi/autocjk-hanzi.rcjk/characterGlyph/backup_wght/uni4F_64.alt00.glif
