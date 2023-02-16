from django.db import models
from django.utils.translation import gettext_lazy as _


class OrderModel(models.Model):
    class Meta:
        abstract = True

    order = models.PositiveSmallIntegerField(
        verbose_name=_("Order"),
        default=0,
    )
