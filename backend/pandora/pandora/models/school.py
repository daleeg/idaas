#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import json
import logging
from django.db import models
from django.utils.translation import ugettext_lazy as _
from pandora.core.models import ExtraCoreModel

LOG = logging.getLogger(__name__)

__all__ = [
    'School',
]


class School(ExtraCoreModel):
    name = models.CharField(help_text=_("名称,str(64)"), max_length=64)
    description = models.TextField(help_text=_('简介'), blank=True, null=True)
    phone = models.CharField(help_text=_("官方电话, str(20)"), max_length=20, blank=True, null=True)
    code = models.CharField(help_text=_("学校唯一标识码, str(64)"), max_length=64, blank=True, null=True)

    province = models.CharField(help_text=_("省, str(20)"), max_length=20)
    city = models.CharField(help_text=_("市, str(20)"), max_length=20)
    area = models.CharField(help_text=_("区, str(20)"), max_length=20)

    avatar = models.CharField(help_text=_("校徽图片访问URL, str(256)"), max_length=256, blank=True, null=True)
    motto = models.CharField(help_text=_("校训, str(256)"), max_length=256, blank=True, null=True)

    principal_name = models.CharField(help_text=_("学校责任人姓名, str(64)"), max_length=64, blank=True, null=True)
    principal_email = models.EmailField(_('学校责任人邮箱'), blank=True, null=True)
    principal_phone = models.CharField(help_text=_("学校责任人电话, str(20)"), max_length=20, blank=True, null=True)

    specific = models.TextField(help_text=_('个性化信息'), blank=True, null=True)
    brief_img = models.CharField(help_text=_('简介图片路径'), max_length=256, blank=True, null=True)
    face_group = models.CharField(help_text=_('人脸组'), max_length=128, blank=True, null=True)

    def __str__(self):
        return "{}".format(self.name)

    def get_extra_info(self, key):
        try:
            specific = json.loads(self.specific)
            value = specific.get(key)
        except (Exception,):
            try:
                format_s = self.specific.replace("'", '"')
                specific = json.loads(format_s)
                value = specific.get(key)
            except (Exception,):
                value = None
        return value

    @property
    def extra(self):
        try:
            format_s = self.specific.replace("'", '"')
            extra = json.loads(format_s)
        except (Exception,):
            extra = {}
        return extra

    @extra.setter
    def extra(self, value):
        if isinstance(value, dict):
            old_value = self.extra
            old_value.update(value)
            self.specific = json.dumps(old_value)
            self.save(update_fields=["specific"])
