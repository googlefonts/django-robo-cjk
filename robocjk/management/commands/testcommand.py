# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'hello'

    def handle(self, *args, **options):
        print('hello')
