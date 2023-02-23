from django.core.management.base import BaseCommand
from django.core.paginator import Paginator

from robocjk.models import CharacterGlyph


class Command(BaseCommand):
    help = "Update all Character Glyphs unicodes (from xml value)."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):
        glifs_queryset = CharacterGlyph.objects.all()
        glifs_paginator = Paginator(glifs_queryset, 1000)

        glif_objs_counter = 0
        glif_objs_updated_counter = 0
        glif_objs_total = CharacterGlyph.objects.count()

        for glifs_page in glifs_paginator:
            glifs_list = glifs_page.object_list

            for glif_obj in glifs_list:
                glif_data = glif_obj._parse_data(glif_obj.data)
                if glif_data:
                    if len(glif_data.unicodes) > 1:
                        glif_obj.save()
                        glif_objs_updated_counter += 1
                glif_objs_counter += 1
                print(
                    f"Updated {glif_objs_counter} ({glif_objs_updated_counter}) "
                    f"of {glif_objs_total} Character Glyphs."
                )
