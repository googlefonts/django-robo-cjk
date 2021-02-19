# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from robocjk.models import Font

import datetime as dt


class Command(BaseCommand):

    help = 'Test font commit message'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        # https://docs.python.org/3/library/argparse.html
        parser.add_argument(
            '--font-uid',
            required=True,
            help='The uid "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" of the font.')

    def handle(self, *args, **options):
        font_uid = options.get('font_uid')
        try:
            font_obj = Font.objects.select_related('project').get(uid=font_uid)
        except Font.DoesNotExist:
            raise CommandError(
                'Invalid font_uid, font with uid "{}" doesn\'t exist.'.format(font_uid))
        commit_message = font_obj.get_commit_message()
        self.stdout.write(commit_message)
