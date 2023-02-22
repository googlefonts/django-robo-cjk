from django.core.management.base import BaseCommand

from robocjk.models import AtomicElement, CharacterGlyph, DeepComponent, StatusModel


class Command(BaseCommand):
    help = "Update all glifs status (from xml value)."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):
        glif_models = [CharacterGlyph, DeepComponent, AtomicElement]
        for glif_model in glif_models:
            # print('Updating {} models.'.format(glif_model))
            glif_objs = glif_model.objects.all()
            glif_objs_counter = 0
            glif_objs_total = len(glif_objs)
            for glif_obj in glif_objs:
                glif_obj_changed = False
                glif_data = glif_obj._parse_data()
                if glif_data:
                    status = StatusModel.get_status_from_data(data=glif_data)
                    if status != glif_obj.status:
                        glif_obj.status = status
                        glif_obj_changed = True
                        # glif_model.objects.filter(pk=glif_obj.pk).update(status=status)
                    # set initial status changed at
                    if not glif_obj.status_changed_at:
                        glif_obj.status_changed_at = glif_obj.updated_at
                        glif_obj.previous_status = glif_obj.status
                        glif_obj_changed = True
                    # save glif model only if some status field changed
                    if glif_obj_changed:
                        glif_obj.save()

                glif_objs_counter += 1
                print(
                    f"Updated {glif_objs_counter} of {glif_objs_total} - {glif_model} models."
                )
