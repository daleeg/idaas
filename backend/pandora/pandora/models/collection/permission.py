# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.utils.translation import ugettext_lazy as _
from pandora.core.models import BaseSet

__all__ = [
    "GroupPermissionLevel",
    "ActionMode",
    "TerminalCategory"
]


class ActionMode(BaseSet):
    READ = 0b100
    WRITE = 0b10
    AUTHORIZE = 0b1
    MESSAGE = {
        READ: _("读"),
        WRITE: _("写"),
        AUTHORIZE: _("授权"),
    }

    @classmethod
    def all(cls):
        return cls.READ | cls.WRITE | cls.AUTHORIZE

    @classmethod
    def none(cls):
        return 0

    @classmethod
    def check(cls, key):
        return key in [0, cls.READ, cls.READ | cls.WRITE, cls.READ | cls.WRITE | cls.AUTHORIZE]

    @classmethod
    def choices(cls):
        return [
            (0, "无权限"),
            (cls.READ, "读权限"),
            (cls.READ | cls.WRITE, "读，写权限"),
            (cls.READ | cls.WRITE | cls.AUTHORIZE, "读, 写, 授权权限"),
        ]


class TerminalCategory(BaseSet):
    PHONE = 0b1
    PAD = 0b10
    MAC = 0b100
    MESSAGE = {
        PHONE: _("手机"),
        PAD: _("平板"),
        MAC: _("笔记本, PC"),
    }

    @classmethod
    def all(cls):
        return cls.PHONE | cls.PAD | cls.MAC

    @classmethod
    def none(cls):
        return 0

    @classmethod
    def check(cls, key):
        return 0 <= key <= cls.PHONE | cls.PAD | cls.MAC


class GroupPermissionLevel(BaseSet):
    LEVEL_COMPANY = 1
    LEVEL_GRADE = 2
    LEVEL_CLASS = 3
    LEVEL_PERSON = 4
    MESSAGE = {
        LEVEL_COMPANY: _("公司级"),
        LEVEL_GRADE: _("年级"),
        LEVEL_CLASS: _("班级"),
        LEVEL_PERSON: _("个人"),
    }
