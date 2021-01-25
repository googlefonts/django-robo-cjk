# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from robocjk.models import (
    CharacterGlyph,
    CharacterGlyphLayer,
    DeepComponent,
    AtomicElement,
    AtomicElementLayer, )


class Command(BaseCommand):

    help = 'Update all glifs relations (relations are built on glif save).'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)


    def handle(self, *args, **options):
        glif_models = [CharacterGlyph, CharacterGlyphLayer, DeepComponent, AtomicElement, AtomicElementLayer]
        for glif_model in glif_models:
            print('Updating {} models.'.format(glif_model))
            glif_objs = glif_model.objects.filter(has_components=True)
            glif_objs_counter = 0
            glif_objs_total = len(glif_objs)
            for glif_obj in glif_objs:
                glif_obj.save()
                glif_objs_counter += 1
                print('Updated {} of {} - {} models.'.format(
                    glif_objs_counter, glif_objs_total, glif_model))