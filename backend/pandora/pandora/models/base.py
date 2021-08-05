#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from pandora.core.models import CoreModel, ExtraCoreModel, MpttCoreModel, MpttExtraCoreModel
from pandora.models import Company
# from django_mysql.models import JSONField, Model

__all__ = [
    "BaseModel",
    "ExtraBaseModel",
    "CoreModel",
    "ExtraCoreModel",
    "ExpandBaseModel",
    "MpttExpandBaseModel",
    "MpttExtraCoreModel"
]


class BaseModel(CoreModel):
    company = models.ForeignKey(Company, to_field="uid", help_text=_("公司"), on_delete=models.SET_NULL,
                                null=True, db_constraint=False)

    class Meta:
        abstract = True


class ExtraBaseModel(ExtraCoreModel):
    company = models.ForeignKey(Company, to_field="uid", help_text=_("公司"), on_delete=models.SET_NULL,
                                null=True, db_constraint=False)

    class Meta:
        abstract = True


class ExpandBaseModel(MpttCoreModel):
    company = models.ForeignKey(Company, to_field="uid", help_text=_("公司"), on_delete=models.SET_NULL,
                                null=True, db_constraint=False)
    expand = models.JSONField(blank=True, null=True, help_text=_("扩展字段"))

    class Meta:
        abstract = True


class MpttExpandBaseModel(MpttExtraCoreModel):
    company = models.ForeignKey(Company, to_field="uid", help_text=_("公司"), on_delete=models.SET_NULL,
                                null=True, db_constraint=False)
    expand = models.JSONField(blank=True, null=True, help_text=_("扩展字段"))

    class Meta:
        abstract = True
