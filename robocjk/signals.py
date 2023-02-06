from django.db.models.signals import post_save, pre_delete


def connect_signals():
    from robocjk.io.client import (
        create_or_update_font,
        create_or_update_project,
        delete_atomic_element,
        delete_atomic_element_layer,
        delete_character_glyph,
        delete_character_glyph_layer,
        delete_deep_component,
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
    # pre_delete.connect(delete_project, sender=Project)

    post_save.connect(create_or_update_font, sender=Font)
    # pre_delete.connect(delete_font, sender=Font)

    # post_save.connect(create_or_update_character_glyph, sender=CharacterGlyph)
    pre_delete.connect(delete_character_glyph, sender=CharacterGlyph)

    # post_save.connect(create_or_update_character_glyph_layer, sender=CharacterGlyphLayer)
    pre_delete.connect(delete_character_glyph_layer, sender=CharacterGlyphLayer)

    # post_save.connect(create_or_update_deep_component, sender=DeepComponent)
    pre_delete.connect(delete_deep_component, sender=DeepComponent)

    # post_save.connect(create_or_update_atomic_element, sender=AtomicElement)
    pre_delete.connect(delete_atomic_element, sender=AtomicElement)

    # post_save.connect(create_or_update_atomic_element_layer, sender=AtomicElementLayer)
    pre_delete.connect(delete_atomic_element_layer, sender=AtomicElementLayer)

    # post_save.connect(create_or_update_proof, sender=Proof)
    # pre_delete.connect(delete_proof, sender=Proof)
