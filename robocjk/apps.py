# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RoboCJKConfig(AppConfig):

    name = 'robocjk'
    verbose_name = _('RoboCJK')

    def ready(self):
        pass
