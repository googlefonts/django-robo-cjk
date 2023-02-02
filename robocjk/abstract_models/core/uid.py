import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _


class UIDModel(models.Model):
    class Meta:
        abstract = True

    uid = models.UUIDField(verbose_name=_("Unique ID"), default=uuid.uuid4, editable=False)
