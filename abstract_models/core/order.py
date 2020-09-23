# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class OrderModel(models.Model):

    class Meta:
        abstract = True

    order = models.PositiveSmallIntegerField(verbose_name=_('Order'), default=0)

