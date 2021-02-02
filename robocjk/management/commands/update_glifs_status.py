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

    help = 'Update all glifs status (from xml value).'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)


    def handle(self, *args, **options):
        glif_models = [CharacterGlyph, DeepComponent, AtomicElement]
        for glif_model in glif_models:
            # print('Updating {} models.'.format(glif_model))
            glif_objs = glif_model.objects.all()
            glif_objs_counter = 0
            glif_objs_total = len(glif_objs)
            for glif_obj in glif_objs:
                glif_data = glif_obj._parse_data()
                if glif_data:
                    status_color = glif_data.status_color
                    status = None
                    if status_color:
                        status = glif_model.STATUS_MARK_COLORS.get(status_color, None)
                    if status is None:
                        status = glif_model.STATUS_WIP
                    if status != glif_obj.status:
                        glif_model.objects.filter(pk=glif_obj.pk).update(status=status)
                glif_objs_counter += 1
                print('Updated {} of {} - {} models.'.format(
                    glif_objs_counter, glif_objs_total, glif_model))
