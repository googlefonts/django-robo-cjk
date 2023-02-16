import time

from django.core.management.base import BaseCommand

from robocjk.models import (
    AtomicElement,
    AtomicElementLayer,
    CharacterGlyph,
    CharacterGlyphLayer,
    DeepComponent,
)


class Command(BaseCommand):
    help = "Test export queries performance"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):
        start_t = time.time()

        font_id = 3

        character_glyphs_qs = (
            CharacterGlyph.objects.select_related("font", "font__project")
            .filter(font_id=font_id)
            .order_by()
        )
        character_glyphs_layers_qs = (
            CharacterGlyphLayer.objects.select_related(
                "glif", "glif__font", "glif__font__project"
            )
            .filter(glif__font_id=font_id)
            .order_by()
        )
        deep_components_qs = (
            DeepComponent.objects.select_related("font", "font__project")
            .filter(font_id=font_id)
            .order_by()
        )
        atomic_elements_qs = (
            AtomicElement.objects.select_related("font", "font__project")
            .filter(font_id=font_id)
            .order_by()
        )
        atomic_elements_layers_qs = (
            AtomicElementLayer.objects.select_related(
                "glif", "glif__font", "glif__font__project"
            )
            .filter(glif__font_id=font_id)
            .order_by()
        )

        all_glifs_qs = [
            character_glyphs_qs,
            character_glyphs_layers_qs,
            deep_components_qs,
            atomic_elements_qs,
            atomic_elements_layers_qs,
        ]

        glifs_list_total = 0
        for glifs_qs in all_glifs_qs:
            glifs_list = list(glifs_qs)
            glifs_list_total += len(glifs_list)

        end_t = time.time()
        diff_t = end_t - start_t
        print(f"Executed all queries on {glifs_list_total} in {diff_t} seconds.")
