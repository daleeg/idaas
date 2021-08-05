# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

# return code
SUCCESS = 0
UNKNOWN_ERROR = 1
BAD_REQUEST = 2
NO_PERMISSION = 3
AUTHENTICATION_FAILED = 4
NOT_AUTHENTICATED = 5
NOT_SUPPORT = 6
DATABASE_ERROR = 7
DATA_CONFLICT = 8
DELETE_FORBIDDEN = 9
LOGIN_FAILED = 10
NOT_FOUND = 11
UPDATE_FORBIDDEN = 12
MULTI_USERS = 13
MISS_PARAMETER = 14
PARAMETER_ERROR = 15
LICENSE_EXPIRING = 16
LICENSE_LIMIT = 17
PHONE_NOT_EXIST = 18
FILE_TOO_LARGE = 19
FILE_NOT_FOUND = 20
MENU_TOO_MANY = 21
MYSQL_GONE_AWAY = 22
NO_COMPANY = 23

# return message
RETURN_MSG = {
    SUCCESS: _("正常"),
    UNKNOWN_ERROR: _("未知错误"),
    BAD_REQUEST: _("错误请求格式"),
    NO_PERMISSION: _("无访问权限"),
    AUTHENTICATION_FAILED: _("用户名或密码错误"),
    NOT_AUTHENTICATED: _("请登录"),
    NOT_SUPPORT: _("不支持"),
    LICENSE_EXPIRING: _("授权已过期或未授权，请联系管理员"),
    LICENSE_LIMIT: _("超过授权账户最大允许的用户数，请联系管理员"),
    NOT_FOUND: _("未查询到"),
    FILE_TOO_LARGE: _("上传文件太大"),
    FILE_NOT_FOUND: _("无法找到文件"),
    DATABASE_ERROR: _("数据库错误"),
    DATA_CONFLICT: _("数据冲突"),
    DELETE_FORBIDDEN: _("禁止删除"),
    LOGIN_FAILED: _("登录失败"),
    MENU_TOO_MANY: _("定制菜单超过数量"),
    MYSQL_GONE_AWAY: _("数据库连接失败"),
    MISS_PARAMETER: _("缺少重要参数"),
    PARAMETER_ERROR: _("参数错误"),
    UPDATE_FORBIDDEN: _("禁止修改"),
    MULTI_USERS: _("存在多个用户"),
    PHONE_NOT_EXIST: _("手机号不存在"),
    NO_COMPANY: _("未传公司参数"),
}
