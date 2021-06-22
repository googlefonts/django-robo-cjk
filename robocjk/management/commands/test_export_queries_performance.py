# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from robocjk.models import *

import datetime as dt

import time


class Command(BaseCommand):

    help = 'Test export queries performance'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):

        start_t = time.time()

        font_id = 3

        character_glyphs_qs = CharacterGlyph.objects.select_related('font', 'font__project').filter(font_id=font_id)
        character_glyphs_layers_qs = CharacterGlyphLayer.objects.select_related('glif', 'glif__font', 'glif__font__project').filter(glif__font_id=font_id)
        deep_components_qs = DeepComponent.objects.select_related('font', 'font__project').filter(font_id=font_id)
        atomic_elements_qs = AtomicElement.objects.select_related('font', 'font__project').filter(font_id=font_id)
        atomic_elements_layers_qs = AtomicElementLayer.objects.select_related('glif', 'glif__font', 'glif__font__project').filter(glif__font_id=font_id)

        all_glifs_qs = [
            character_glyphs_qs, character_glyphs_layers_qs,
            deep_components_qs,
            atomic_elements_qs, atomic_elements_layers_qs,
        ]

        for glifs_qs in all_glifs_qs:
            glifs_list = list(glifs_qs)

        end_t = time.time()

        print('Executed all queries in {} seconds.'.format(end_t - start_t))

