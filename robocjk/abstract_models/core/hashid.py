from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from hashids import Hashids


class HashidModel(models.Model):
    class Meta:
        abstract = True

    hashid = models.CharField(
        verbose_name=_("Hash ID"),
        db_index=True,
        max_length=50,
        blank=True,
        editable=False,
    )

    def _update_hashid(self):
        if self.pk:
            # get hashids options from settings and fallback to some defaults
            hashids_options = getattr(settings, "HASHIDS_OPTIONS", {})
            hashids_options.setdefault("salt", "django")
            hashids_options.setdefault(
                "alphabet", "abcdefghijklmnopqrstuvwxyz0123456789"
            )
            hashids_options.setdefault("min_length", 8)
            hashids = Hashids(**hashids_options)
            hashid = hashids.encode(self.pk, 1)
            if hashid != self.hashid:
                self.hashid = hashid
                self.__class__.objects.filter(pk=self.pk).update(hashid=hashid)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_hashid()
