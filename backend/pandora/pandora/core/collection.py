# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from pandora.core.models import BaseSet

__all__ = [
    "ScaleSet",
]


class ScaleSet(BaseSet):
    MICRO = "micro"
    GENERAL = "general"
    DETAIL = "detail"
    CREATE = "create"
    UPDATE = "update"
    DESTROY = "destroy"

    MESSAGE = {
        MICRO: _("微型"),
        GENERAL: _("普通"),
        DETAIL: _("详细"),
        CREATE: _("创建"),
        UPDATE: _("修改"),
        DESTROY: _("销毁"),
    }

    @classmethod
    def query_choices(cls):
        query_scales = [cls.MICRO, cls.GENERAL, cls.DETAIL]
        return [(s, cls.MESSAGE[s]) for s in query_scales]
