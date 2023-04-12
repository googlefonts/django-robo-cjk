import fsutil
from django.core.management.base import BaseCommand

from robocjk.models import (  # AtomicElement, CharacterGlyph, DeepComponent, StatusModel
    CharacterGlyphLayer,
    Font,
)


class Command(BaseCommand):
    help = "Check glifs."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):
        glif_files = fsutil.search_files("/root/.rcjks/", "**/*.glif")
        print(len(glif_files))

        return
        font = Font.objects.get(id=49)
        print(font.project, font)
        layers = CharacterGlyphLayer.objects.select_related(
            "glif", "glif__font"
        ).filter(glif__font=font)
        print(len(layers))
        layers_filepaths_list = [layer.path() for layer in layers]
        print(len(layers_filepaths_list))
        layers_filepaths_set = set(layers_filepaths_list)
        print(len(layers_filepaths_set))

        layers_path = "/root/.rcjks/gs-flex-cjk/hanzi.rcjk/characterGlyph/"
        layers_dirs = fsutil.list_dirs(layers_path)
        layers_files_list = []
        for layer_dir in layers_dirs:
            # print(layer_dir)
            layers_files_list += fsutil.search_files(layer_dir, "*.glif")
        # print(len(layers_files_list))
        layers_files_set = set(layers_files_list)

        layers_files_unexpected = layers_files_set - layers_filepaths_set
        for layer_file in layers_files_unexpected:
            print(layer_file)
