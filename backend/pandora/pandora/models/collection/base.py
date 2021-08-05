from django.utils.translation import ugettext_lazy as _
from pandora.core.models import BaseSet

__all__ = [
    "VirtualUserRoleSet",
    "DataOriginSet",
    "AppPlatform",
    "AuthType",
    "SyncType",
    "MappingField",
    "CommonStatus",
    "ExpandFieldCategory",
    "FieldType",
]


class VirtualUserRoleSet(BaseSet):
    DEVICE = 11
    SUPPER = 12
    CLIENT = 13
    DEVELOPER_APP = 14

    MESSAGE = {
        DEVICE: _("设备"),
        SUPPER: _("超级用户"),
        CLIENT: _("超级APP用户"),
        DEVELOPER_APP: _("开发者应用用户"),
    }

from django.conf import global_settings
class DataOriginSet(BaseSet):
    SELF = 1
    EXTERNAL = 2
    SYSTEM = 3

    MESSAGE = {
        SELF: _("自建数据"),
        EXTERNAL: _("外部数据"),
        SYSTEM: _("系统数据"),
    }

    @classmethod
    def create_choices(cls):
        return [[cls.EXTERNAL, cls.MESSAGE[cls.EXTERNAL]]]


class AppPlatform(BaseSet):
    WEB = 1
    PHONE = 2

    MESSAGE = {
        WEB: _("网站"),
        PHONE: _("手机"),
    }


class AuthType(BaseSet):
    HTTP = 1
    OAUTH2 = 2
    SAML = 3
    OIDC = 4
    CAS = 5
    MESSAGE = {
        HTTP: _("http"),
        OAUTH2: _("OAuth2"),
        SAML: _("SAML"),
        OIDC: _("OIDC"),
        CAS: _("CAS"),
    }


class SyncType(BaseSet):
    DISABLE = 1
    SCIM = 2
    MESSAGE = {
        DISABLE: _("未启用"),
        SCIM: _("SCIM"),
    }


class MappingField(BaseSet):
    CUSTOM = 1
    USERNAME = 2
    EMAIL = 3
    PHONE = 4
    NUMBER = 5

    MESSAGE = {
        CUSTOM: _("自定义"),
        USERNAME: _("USERNAME"),
        EMAIL: _("EMAIL"),
        PHONE: _("PHONE"),
        NUMBER: _("NUMBER"),
    }


class CommonStatus(BaseSet):
    DISABLE = 0
    ENABLE = 1

    MESSAGE = {
        DISABLE: _("禁用"),
        ENABLE: _("启用"),
    }


class ExpandFieldCategory(BaseSet):
    TEACHER = 1
    STUDENT = 2
    CONTACT = 3
    GROUP = 4
    ORGANIZATION = 5
    SECTION = 6

    MESSAGE = {
        TEACHER: _("教师"),
        STUDENT: _("学生"),
        CONTACT: _("家长"),
        GROUP: _("用户组"),
        ORGANIZATION: _("组织机构"),
        SECTION: _("班级"),
    }


class FieldType(BaseSet):
    STRING = 1
    DATE = 2
    BOOL = 3
    INT = 4
    FLOAT = 5

    MESSAGE = {
        STRING: _("字符串"),
        DATE: _("日期"),
        BOOL: _("布尔值"),
        INT: _("整数"),
        FLOAT: _("浮点值"),
    }
