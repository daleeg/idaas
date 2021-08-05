# -*- coding: utf-8 -*-
import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _
from pandora.core.models.core import ExtraCoreModel

LOG = logging.getLogger(__name__)

__all__ = [
    "Company",
]


class Company(ExtraCoreModel):
    name = models.CharField(db_index=True, max_length=64, help_text=_("名称"))
    code = models.CharField(db_index=True, max_length=32, help_text=_("标识码"))
    description = models.TextField(blank=True, null=True, help_text=_("简介"))
    extra_info = models.TextField(blank=True, null=True, help_text=_("可扩展属性"))

    def __str__(self):
        return "{}".format(self.name)

