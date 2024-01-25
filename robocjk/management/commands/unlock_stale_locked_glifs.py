import logging
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from robocjk.models import AtomicElement, CharacterGlyph, DeepComponent, Font

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Unlock stale locked glifs."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):
        error_message = ""

        now = datetime.now()
        now_with_delta = now - timedelta(hours=48)

        fonts_qs = Font.objects.all()
        glif_models = [
            CharacterGlyph,
            DeepComponent,
            AtomicElement,
        ]
        for font_obj in fonts_qs:
            for glif_model in glif_models:
                glif_objs_qs = glif_model.objects.filter(
                    font=font_obj,
                    is_locked=True,
                    locked_at__lt=now_with_delta,
                    updated_at__lt=now_with_delta,
                )
                if glif_objs_qs.exists():
                    glif_objs_count = glif_objs_qs.count()
                    glif_objs_unlocked_pks = []
                    for glif_obj in glif_objs_qs:
                        glif_obj.unlock_by(
                            user=None,
                            save=True,
                            force=True,
                        )
                        glif_objs_unlocked_pks.append(glif_obj.pk)
                    glif_objs_unlocked_pks_str = ", ".join(
                        map(str, glif_objs_unlocked_pks)
                    )

                    error_message += (
                        f"- {font_obj} / {glif_model.__name__}s\n"
                        f"  Unlocked {glif_objs_count} stale locked glifs\n"
                        f"  IDs: {glif_objs_unlocked_pks_str}\n"
                        f"\n"
                    )

        if error_message:
            logger.error(error_message)
