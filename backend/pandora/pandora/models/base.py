#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.db import models
from pandora.core.models import CoreModel, ExtraCoreModel
from pandora.models import School

__all__ = [
    "BaseModel",
    "ExtraBaseModel",
    "CoreModel",
    "ExtraCoreModel",
]


class BaseModel(CoreModel):
    school = models.ForeignKey(School, to_field="uid", help_text=_("学校"), on_delete=models.SET_NULL,
                               blank=True, null=True)

    class Meta:
        abstract = True


class ExtraBaseModel(ExtraCoreModel):
    school = models.ForeignKey(School, to_field="uid", help_text=_("学校"), on_delete=models.SET_NULL,
                               blank=True, null=True)

    class Meta:
        abstract = True
