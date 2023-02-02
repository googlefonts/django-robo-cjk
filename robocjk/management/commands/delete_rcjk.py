from django.core.management.base import BaseCommand, CommandError

from robocjk.models import Font


class Command(BaseCommand):
    help = "Delete .rcjk project"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        # https://docs.python.org/3/library/argparse.html
        parser.add_argument(
            "--font-uid",
            required=True,
            help='The uid "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" of the font that will be deleted.',
        )

    def handle(self, *args, **options):
        font_uid = options.get("font_uid")
        try:
            font_obj = Font.objects.select_related("project").get(uid=font_uid)
        except Font.DoesNotExist:
            raise CommandError(
                'Invalid font_uid, font with uid "{}" doesn\'t exist.'.format(font_uid)
            )

        font_obj.available = False
        font_obj.save()
        font_obj.delete()
