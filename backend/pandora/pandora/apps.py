# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig

__all__ = ["PandoraConfig"]


class PandoraConfig(AppConfig):
    name = "pandora"
    verbose_name = "pandora"

    def ready(self):
        import pandora.utils.parallel
        import pandora.signal

