from django.db.models.signals import post_save, pre_delete


def connect_signals():
    from robocjk.io.client import (
        create_or_update_font,
        create_or_update_project,
        delete_glif,
    )
    from robocjk.models import (
        AtomicElement,
        AtomicElementLayer,
        CharacterGlyph,
        CharacterGlyphLayer,
        DeepComponent,
        Font,
        Project,
    )

    post_save.connect(create_or_update_project, sender=Project)
    post_save.connect(create_or_update_font, sender=Font)
    pre_delete.connect(delete_glif, sender=CharacterGlyph)
    pre_delete.connect(delete_glif, sender=CharacterGlyphLayer)
    pre_delete.connect(delete_glif, sender=DeepComponent)
    pre_delete.connect(delete_glif, sender=AtomicElement)
    pre_delete.connect(delete_glif, sender=AtomicElementLayer)
