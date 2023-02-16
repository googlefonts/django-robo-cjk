import zipfile

import fsutil
from benedict import benedict
from django.core.management.base import BaseCommand, CommandError
from extra_settings.models import Setting

from robocjk.core import GlifData
from robocjk.io.paths import (
    ATOMIC_ELEMENT_LAYER_RE,
    ATOMIC_ELEMENT_RE,
    CHARACTER_GLYPH_LAYER_RE,
    CHARACTER_GLYPH_RE,
    DEEP_COMPONENT_RE,
    DESIGNSPACE_RE,
    FEATURES_RE,
    FONTLIB_RE,
    unquote_filename,
)
from robocjk.models import (
    AtomicElement,
    AtomicElementLayer,
    CharacterGlyph,
    CharacterGlyphLayer,
    DeepComponent,
    Font,
    StatusModel,
)


class Command(BaseCommand):
    help = "Import .rcjk project"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._import_mappings = [
            {
                "path_regex": CHARACTER_GLYPH_RE,
                "group_name": "character_glyphs",
                "import_func": self._import_character_glyph,
            },
            {
                "path_regex": CHARACTER_GLYPH_LAYER_RE,
                "group_name": "character_glyphs_layers",
                "import_func": self._import_character_glyph_layer,
            },
            {
                "path_regex": DEEP_COMPONENT_RE,
                "group_name": "deep_components",
                "import_func": self._import_deep_component,
            },
            {
                "path_regex": ATOMIC_ELEMENT_RE,
                "group_name": "atomic_elements",
                "import_func": self._import_atomic_element,
            },
            {
                "path_regex": ATOMIC_ELEMENT_LAYER_RE,
                "group_name": "atomic_elements_layers",
                "import_func": self._import_atomic_element_layer,
            },
            {
                "path_regex": FONTLIB_RE,
                "group_name": "fontlib",
                "import_func": self._import_fontlib,
            },
            {
                "path_regex": FEATURES_RE,
                "group_name": "features",
                "import_func": self._import_features,
            },
            {
                "path_regex": DESIGNSPACE_RE,
                "group_name": "designspace",
                "import_func": self._import_designspace,
            },
        ]

        self._import_groups = {item["group_name"]: [] for item in self._import_mappings}

    def add_arguments(self, parser):
        # https://docs.python.org/3/library/argparse.html
        parser.add_argument(
            "--filepath",
            required=True,
            help='The zipped .rcjk filepath. The filepath must be absolute or relative to "/root/robocjk/temp/"',
        )
        parser.add_argument(
            "--font-uid",
            required=True,
            help='The uid "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" of the font into which the .rcjk files will be imported.',
        )
        parser.add_argument(
            "--font-clear",
            action="store_true",
            help="Delete existing Atomic Elements, Atomic Elements Layers, Deep Components, "
            "Character Glyphs, Character Glyphs Layers before importing new .rcjk file.",
        )

    def handle(self, *args, **options):  # noqa: C901
        import_enabled = Setting.get("ROBOCJK_IMPORT_ENABLED", default=True)
        if not import_enabled:
            message = "Import has been disabled through the 'ROBOCJK_IMPORT_ENABLED' setting in the admin."
            self.stderr.write(message)
            raise CommandError(message)

        filepath = options.get("filepath")
        if not filepath.startswith("/"):
            filepath = fsutil.join_path("/root/robocjk/temp/", filepath)
        if not filepath.endswith(".zip"):
            message = (
                "Invalid filepath, expected a .zip file containing .rcjk font project."
            )
            self.stderr.write(message)
            raise CommandError(message)
        if not fsutil.exists(filepath):
            message = f'Invalid filepath, file "{filepath}" doesn\'t exist.'
            self.stderr.write(message)
            raise CommandError(message)

        font_uid = options.get("font_uid")
        try:
            font_obj = Font.objects.select_related("project").get(uid=font_uid)
        except Font.DoesNotExist:
            message = 'Invalid font_uid, font with uid "{}" doesn\'t exist.'.format(
                font_uid
            )
            self.stderr.write(message)
            raise CommandError(message)

        self.stdout.write(f'Importing "{font_obj.name}"...')

        if font_obj.export_running:
            message = 'There is an export running for "{}", the import will run on export complete.'.format(
                font_obj.name
            )
            self.stderr.write(message)
            raise CommandError(message)

        font_obj.available = False
        font_obj.save()

        font_clear = options.get("font_clear", False)
        if font_clear:
            self.stdout.write("Deleting existing atomic elements...")
            AtomicElement.objects.filter(font__uid=font_uid).delete()
            self.stdout.write("Deleting existing deep components...")
            DeepComponent.objects.filter(font__uid=font_uid).delete()
            self.stdout.write("Deleting existing character glyphs...")
            CharacterGlyph.objects.filter(font__uid=font_uid).delete()

        # read and index zip files by type
        with zipfile.ZipFile(filepath, "r") as file:
            names = file.namelist()

            for name in names:
                for item in self._import_mappings:
                    match = item["path_regex"].match(name)
                    if match:
                        self._import_groups[item["group_name"]].append(
                            (
                                name,
                                match,
                            )
                        )
                        continue

            for item in self._import_mappings:
                group_name = item["group_name"]
                self.stdout.write(
                    "Found {} {} to import.".format(
                        len(self._import_groups[group_name]),
                        group_name.replace("_", " ").title(),
                    )
                )

            for item in self._import_mappings:
                for name, match in self._import_groups[item["group_name"]]:
                    item["import_func"](font_obj, self._zipfile_read(file, name), match)

        # update deep-components relations with atomic-elements
        glif_objs = font_obj.deep_components.filter(has_components=True)
        glif_objs_counter = 0
        glif_objs_total = len(glif_objs)
        self.stdout.write(f"Updating {glif_objs_total} DeepComponent relations...")
        for glif_obj in glif_objs:
            glif_obj.save()
            glif_objs_counter += 1
            # self.stdout.write('Updated DeepComponent relations - {} of {}'.format(glif_objs_counter, glif_objs_total))
        self.stdout.write(f"Updated {glif_objs_total} DeepComponent relations.")

        # update character-glyphs relations with deep-components
        glif_objs = font_obj.character_glyphs.filter(has_components=True)
        glif_objs_counter = 0
        glif_objs_total = len(glif_objs)
        self.stdout.write(f"Updating {glif_objs_total} CharacterGlyphs relations...")
        for glif_obj in glif_objs:
            glif_obj.save()
            glif_objs_counter += 1
            # self.stdout.write('Updated CharacterGlyph relations - {} of {}'.format(glif_objs_counter, glif_objs_total))
        self.stdout.write(f"Updated {glif_objs_total} CharacterGlyphs relations.")

        font_obj.available = True
        font_obj.save()

    def _zipfile_read(self, file, path, encoding="utf-8"):
        return str(file.read(path), encoding)

    def _import_fontlib(self, font, content, match):
        font.fontlib = benedict.from_json(content, keypath_separator=None)
        font.save()

    def _import_features(self, font, content, match):
        font.features = content
        font.save()

    def _import_designspace(self, font, content, match):
        font.designspace = benedict.from_json(content, keypath_separator=None)
        font.save()

    def _import_glif(self, cls, font, content, match):
        data = GlifData()
        data.parse_string(content)
        # parse status during import
        status = StatusModel.get_status_from_data(data)
        obj, created = cls.objects.update_or_create(
            font=font, name=data.name, defaults={"status": status, "data": content}
        )
        # self.stdout.write('Imported {}: {}'.format(cls, data.name))

    def _import_glif_layer(self, glif_cls, cls, font, content, match):
        data = GlifData()
        data.parse_string(content)
        layer_name = match.groupdict()["layer_name"]
        layer_name = unquote_filename(layer_name)
        try:
            glif_obj = glif_cls.objects.get(font=font, name=data.name)
        except glif_cls.DoesNotExist:
            self.stderr.write(f"Import Error {cls} [{layer_name}]: {data.name}")
            return
        obj, created = cls.objects.update_or_create(
            glif=glif_obj, group_name=layer_name, defaults={"data": content}
        )
        # self.stdout.write('Imported {} [{}]: {}'.format(cls, layer_name, data.name))

    def _import_atomic_element(self, font, content, match):
        self._import_glif(AtomicElement, font, content, match)

    def _import_atomic_element_layer(self, font, content, match):
        self._import_glif_layer(AtomicElement, AtomicElementLayer, font, content, match)

    def _import_deep_component(self, font, content, match):
        self._import_glif(DeepComponent, font, content, match)

    def _import_character_glyph(self, font, content, match):
        self._import_glif(CharacterGlyph, font, content, match)

    def _import_character_glyph_layer(self, font, content, match):
        self._import_glif_layer(
            CharacterGlyph, CharacterGlyphLayer, font, content, match
        )
