# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.core.paginator import Paginator

from robocjk.models import (
    AtomicElement,
    CharacterGlyph,
)


class Command(BaseCommand):

    help = 'Update all glifs layers_updated_at field.'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        # update atomic elements
        atomic_elements_qs = AtomicElement.objects.defer("data").all()
        self._update_layers_updated_at(queryset=atomic_elements_qs)
        # update character glyphs
        character_glyphs_qs = CharacterGlyph.objects.defer("data").all()
        self._update_layers_updated_at(queryset=character_glyphs_qs)


    def _update_layers_updated_at(self, queryset):
        objs_qs = queryset
        objs_count = queryset.count()
        objs_counter = 0
        objs_min_id = 0
        objs_max_id = objs_qs.order_by("-id")[:1].first().id
        objs_per_page = 500
        while True:
            objs_list = list(objs_qs.filter(id__gt=objs_min_id)[:objs_per_page])
            if not objs_list:
                break
            for obj in objs_list:
                obj.update_layers_updated_at()
            objs_counter += len(objs_list)
            objs_min_id = objs_list[-1].id
            print(f"Updated {objs_counter} of {objs_count} glifs.")
