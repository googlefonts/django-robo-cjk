# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.core.paginator import Paginator

from robocjk.models import (
    CharacterGlyphLayer,
    AtomicElementLayer,
)


class Command(BaseCommand):

    help = 'Update all glifs layers_updated_at field.'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

#     # becomes slow because of MySQL large offset
#     def handle(self, *args, **options):
#
#         cg_layers_qs = CharacterGlyphLayer.objects.select_related("glif").defer("data").all()
#         cg_layers_count = cg_layers_qs.count()
#
#         ae_layers_qs = AtomicElementLayer.objects.select_related("glif").defer("data").all()
#         ae_layers_count = ae_layers_qs.count()
#
#         layers_counter = 0
#         layers_count = cg_layers_count + ae_layers_count
#         layers_per_page = 500
#         layers_paginators = [
#             Paginator(cg_layers_qs, glifs_per_page),
#             Paginator(ae_layers_qs, glifs_per_page),
#         ]
#
#         for layers_paginator in layers_paginators:
#             for layers_page in layers_paginator:
#                 layers_list = layers_page.object_list
#                 for layer_obj in layers_list:
#                     glif_obj = layer_obj.glif
#                     if not glif_obj.layers_updated_at or glif_obj.updated_at < layer_obj.updated_at:
#                         layer_obj.update_glif_layers_updated_at()
#                     layers_counter += 1
#                 print(f"Updated {glifs_counter} of {glifs_count} glifs.")

    def handle(self, *args, **options):
        # update atomic elements layers
        atomic_element_layers_qs = AtomicElementLayer.objects.defer("data").all()
        self._update_layers(queryset=atomic_element_layers_qs)
        # update character glyphs layers
        character_glyphs_layers_qs = CharacterGlyphLayer.objects.defer("data").all()
        self._update_layers(queryset=character_glyphs_layers_qs)


    def _update_layers(self, queryset):
        layers_qs = queryset
        layers_count = layers_qs.count()
        layers_counter = 0
        layers_min_id = 0
        layers_max_id = layers_qs.order_by("-id")[:1].first().id
        layers_per_page = 500
        while True:
            layers_list = list(layers_qs.filter(id__gt=layers_min_id).order_by("id")[:layers_per_page])
            if not layers_list:
                break
            layers_counter += len(layers_list)
            # layers_min_id += layers_per_page
            for layer_obj in layers_list:
                glif_obj = layer_obj.glif
                if not glif_obj.layers_updated_at or glif_obj.updated_at < layer_obj.updated_at:
                    # layer_obj.update_glif_layers_updated_at()
                    glif_obj.layers_updated_at = layer_obj.updated_at
                    glif_obj.save()
            layers_min_id = layers_list[-1].id
            print(f"Updated {layers_counter} of {layers_count} glifs.")
