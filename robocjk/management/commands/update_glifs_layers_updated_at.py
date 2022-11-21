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

    def handle(self, *args, **options):

        cg_layers_qs = CharacterGlyphLayer.objects.select_related("glif").defer("data").all()
        cg_layers_count = cg_layers_qs.count()

        ae_layers_qs = AtomicElementLayer.objects.select_related("glif").defer("data").all()
        ae_layers_count = ae_layers_qs.count()

        glifs_counter = 0
        glifs_count = cg_layers_count + ae_layers_count
        glifs_per_page = 500
        glifs_paginators = [
            Paginator(cg_layers_qs, glifs_per_page),
            Paginator(ae_layers_qs, glifs_per_page),
        ]

        for glifs_paginator in glifs_paginators:
            for glifs_page in glifs_paginator:
                glifs_list = glifs_page.object_list
                for glif_obj in glifs_list:
                    if glif_obj.updated_at > glif_obj.glif.updated_at:
                        glif_obj.update_glif_layers_updated_at()
                    glifs_counter += 1
                print(f"Updated {glifs_counter} of {glifs_count} glifs.")
