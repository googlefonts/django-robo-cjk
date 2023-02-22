from django.core.management.base import BaseCommand

from robocjk.models import (
    AtomicElement,
    AtomicElementLayer,
    CharacterGlyph,
    CharacterGlyphLayer,
    DeepComponent,
)


class Command(BaseCommand):
    help = "Update all glifs relations (relations are built on glif save)."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):
        glif_models = [
            CharacterGlyph,
            CharacterGlyphLayer,
            DeepComponent,
            AtomicElement,
            AtomicElementLayer,
        ]
        for glif_model in glif_models:
            print(f"Updating {glif_model} models.")
            glif_objs = glif_model.objects.filter(has_components=True)
            glif_objs_counter = 0
            glif_objs_total = len(glif_objs)
            for glif_obj in glif_objs:
                glif_obj.save()
                glif_objs_counter += 1
                print(
                    f"Updated {glif_objs_counter} of {glif_objs_total} - {glif_model} models."
                )
