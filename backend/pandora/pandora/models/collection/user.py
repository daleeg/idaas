# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from pandora.core.models import BaseSet

__all__ = [
    "UserRoleSet",
    "UserGenderSet",
    "PasswordComplexitySet",
    "USER_DEFAULT_PASSWORD",

]


class UserRoleSet(BaseSet):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    GENERAL = "general"
    DEVELOPER = "developer"
    GUEST = "guest"

    MESSAGE = {
        SUPERADMIN: _("超级管理员"),
        ADMIN: _("管理员"),
        GENERAL: _("普通用戶"),
        GUEST: _("访客"),
        DEVELOPER: _("开发者"),
    }

    @classmethod
    def all_users(cls):
        return [cls.SUPERADMIN, cls.ADMIN, cls.GENERAL, cls.GUEST, cls.DEVELOPER]


class UserGenderSet(BaseSet):
    UNKNOWN = "NA"
    MALE = "M"
    FEMALE = "F"

    MESSAGE = {
        UNKNOWN: _("未知"),
        MALE: _("男"),
        FEMALE: _("女"),
    }


class PasswordComplexitySet(BaseSet):
    NO_LIMIT = 0
    LETTER_NUMBER = 1
    UPPER_NUMBER = 2
    LETTER_NUMBER_SPECIAL = 3

    MESSAGE = {
        NO_LIMIT: _("无特殊限制"),
        LETTER_NUMBER: _("数字和字母"),
        UPPER_NUMBER: _("数字和大写字母"),
        LETTER_NUMBER_SPECIAL: _("数字，字母和特殊字符"),
    }


USER_DEFAULT_PASSWORD = settings.USER_DEFAULT_PASSWORD
