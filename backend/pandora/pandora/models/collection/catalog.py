# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _
from pandora.core.models import BaseSet


class CatalogCategorySet(BaseSet):
    MENU = "menu"
    MODULE = "module"

    MESSAGE = {
        MENU: _("左侧菜单"),
        MODULE: _("右侧页面模块"),
    }
