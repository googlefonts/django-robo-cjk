from django.core.management.base import BaseCommand, CommandError

from robocjk.models import (
    AtomicElement,
    AtomicElementLayer,
    CharacterGlyph,
    CharacterGlyphLayer,
    DeepComponent,
    Font,
)


class Command(BaseCommand):
    help = "Duplicate .rcjk font"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        # https://docs.python.org/3/library/argparse.html
        parser.add_argument(
            "--source-font-uid",
            required=True,
            help="The uid 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx' of the font to duplicate (source).",
        )
        parser.add_argument(
            "--target-font-uid",
            required=True,
            help="The uid 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx' of the font duplicated (target).",
        )
        parser.add_argument(
            "--target-font-clear",
            action="store_true",
            help="Delete existing Atomic Elements, Atomic Elements Layers, Deep Components, "
            "Character Glyphs, Character Glyphs Layers before duplicating source font.",
        )

    def handle(self, *args, **options):  # noqa: C901
        source_font_uid = options.get("source_font_uid")
        try:
            source_font_obj = Font.objects.get(uid=source_font_uid)
        except Font.DoesNotExist as font_error:
            message = f"Invalid source_font_uid, font with uid '{source_font_uid}' doesn't exist."
            self.stderr.write(message)
            raise CommandError(message) from font_error

        target_font_uid = options.get("target_font_uid")
        try:
            target_font_obj = Font.objects.get(uid=target_font_uid)
        except Font.DoesNotExist as font_error:
            message = f"Invalid target_font_uid, font with uid '{target_font_uid}' doesn't exist."
            self.stderr.write(message)
            raise CommandError(message) from font_error

        target_font_clear = options.get("target_font_clear")
        if target_font_clear:
            message = "Unsupported option target_font_clear (not implemented yet, TODO)"
            raise CommandError(message)

        source_project_obj = source_font_obj.project
        if source_project_obj.export_running:
            message = f"Unable to duplicate font, there is an export running for '{source_project_obj.name}'."
            self.stderr.write(message)
            raise CommandError(message)

        target_project_obj = target_font_obj.project
        if target_project_obj.export_running:
            message = f"Unable to duplicate font, there is an export running for '{target_project_obj.name}'."
            self.stderr.write(message)
            raise CommandError(message)

        self.stdout.write(
            f"Duplicating font '{source_project_obj.name} / {source_font_obj.name}' "
            f"-> '{target_project_obj.name} / {target_font_obj.name}'"
        )

        # duplicate font
        font_obj = source_font_obj
        font_clone_obj = target_font_obj
        self.stdout.write(f"Duplicating font '{font_obj.name}' ...")

        self.stdout.write("Duplicating atomic elements and atomic elements layers ...")
        for ae_obj in font_obj.atomic_elements.all():
            ae_clone_obj, _ = AtomicElement.objects.get_or_create(
                font=font_clone_obj,
                name=ae_obj.name,
                defaults={
                    "data": ae_obj.data,
                },
            )
            for ae_layer_obj in ae_obj.layers.all():
                ae_layer_clone_obj, _ = AtomicElementLayer.objects.get_or_create(
                    glif=ae_clone_obj,
                    group_name=ae_layer_obj.group_name,
                    defaults={
                        "data": ae_layer_obj.data,
                    },
                )

        self.stdout.write("Duplicating deep components ...")
        for dc_obj in font_obj.deep_components.all():
            dc_clone_obj, _ = DeepComponent.objects.get_or_create(
                font=font_clone_obj,
                name=dc_obj.name,
                defaults={
                    "data": dc_obj.data,
                },
            )

        self.stdout.write(
            "Duplicating character glyphs and character glyphs layers ..."
        )
        for cg_obj in font_obj.character_glyphs.all():
            cg_clone_obj, _ = CharacterGlyph.objects.get_or_create(
                font=font_clone_obj,
                name=cg_obj.name,
                defaults={
                    "data": cg_obj.data,
                },
            )
            for cg_layer_obj in cg_obj.layers.all():
                cg_layer_clone_obj, _ = CharacterGlyphLayer.objects.get_or_create(
                    glif=cg_clone_obj,
                    group_name=cg_layer_obj.group_name,
                    defaults={
                        "data": cg_layer_obj.data,
                    },
                )

        self.stdout.write("Updating atomic elements many to many relations ...")
        for ae_obj in font_clone_obj.atomic_elements.all():
            ae_obj.update_components()

        self.stdout.write("Updating deep components many to many relations ...")
        for dc_obj in font_clone_obj.deep_components.all():
            dc_obj.update_components()

        self.stdout.write("Updating character glyphs many to many relations ...")
        for cg_obj in font_clone_obj.character_glyphs.all():
            cg_obj.update_components()
