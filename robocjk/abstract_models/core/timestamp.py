from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_(
            "Created at",
        ),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name=_(
            "Updated at",
        ),
    )

    updated_by = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Updated by"),
    )

    editors = models.ManyToManyField(
        get_user_model(),
        related_name="+",
        verbose_name=_("Editors"),
    )

    editors_history = models.TextField(
        blank=True,
        verbose_name=_("Editors History"),
    )

    def update_editors_history(self, user):
        editor_name = user.get_full_name()
        editors_separator = ", "
        editors_list = list(filter(None, self.editors_history.split(editors_separator)))
        # editors_list = [editor for editor in editors_list if slugify(editor) != slugify(editor_name)]
        if not editors_list or editor_name != editors_list[-1]:
            editors_list.append(editor_name)
            if len(editors_list) > 100:
                # TODO: last 100 items
                pass
            self.editors_history = editors_separator.join(editors_list)

    def save_by(self, user):
        # if user and user.id != self.updated_by_id:
        self.update_editors_history(user)
        self.updated_by = user
        self.save()
        self.editors.add(user)
