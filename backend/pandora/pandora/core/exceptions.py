# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import APIException
from rest_framework import status
import demjson
from pandora.core.code import NO_PERMISSION, NOT_AUTHENTICATED, AUTHENTICATION_FAILED, RETURN_MSG
from pandora.core.code import LICENSE_LIMIT, LICENSE_EXPIRING, NO_COMPANY


class BaseException(APIException):
    status_code = status.HTTP_200_OK  # always 200

    def __init__(self, code, message=None):
        self.detail = {"code": code, "message": message or RETURN_MSG[code]}

    def __str__(self):
        return "{}".format(self.detail)


class DataException(BaseException):
    status_code = status.HTTP_200_OK  # always 200

    def __init__(self, code, message=None, data=None):
        self.message = "{}, {}".format(code, message)
        # data = demjson.encode(data) if data else None
        self.detail = {"code": code, "message": message or RETURN_MSG[code], "data": data}

    def __str__(self):
        return self.message


class AuthenticationFailed(BaseException):
    def __init__(self, message=None):
        self.detail = {"code": AUTHENTICATION_FAILED, "message": message or _("认证错误。")}


class NotAuthenticated(BaseException):
    def __init__(self, ):
        self.detail = {"code": NOT_AUTHENTICATED, "message": _("请登录。")}


class PermissionDenied(BaseException):
    def __init__(self, message=None, code=NO_PERMISSION):
        if message:
            self.detail = {"code": NO_PERMISSION, "message": message}
        else:
            self.detail = {"code": NO_PERMISSION, "message": _("无访问权限。")}


class NoCompanyPermissionDenied(BaseException):
    def __init__(self, message=None, code=NO_COMPANY):
        if message:
            self.detail = {"code": NO_COMPANY, "message": message}
        else:
            self.detail = {"code": NO_COMPANY, "message": RETURN_MSG[NO_COMPANY]}


class LicenseLimitOut(BaseException):
    def __init__(self, message=None):
        if message:
            self.detail = {"code": LICENSE_LIMIT, "message": _("{}".format(message))}
        else:
            self.detail = {"code": LICENSE_LIMIT, "message": RETURN_MSG[LICENSE_LIMIT]}


class LicenseExpiring(BaseException):
    def __init__(self, message=None):
        if message:
            self.detail = {"code": LICENSE_EXPIRING, "message": _("{}".format(message))}
        else:
            self.detail = {"code": LICENSE_EXPIRING, "message": RETURN_MSG[LICENSE_EXPIRING]}


class CreateError(Exception):
    pass


class NetworkError(Exception):
    pass


class FetchError(Exception):
    pass


class UpdateError(Exception):
    pass


class DeleteError(Exception):
    pass


class EmptyDataError(Exception):
    pass


class FileEncodeError(Exception):
    pass


class DataEmptyError(Exception):
    pass


class DataInvalidError(Exception):
    def __init__(self, message):
        super(DataInvalidError, self).__init__()
        self.message = message


class DeleteProtectedError(Exception):
    def __init__(self, model_name=None, field=None, message=None):
        super(DeleteProtectedError, self).__init__()
        protect_map = {}
        try:
            self.message = message or _("无法删除{0},原因: {0}与{1}存在关联关系".format(model_name, protect_map[field]))
        except (Exception,):
            self.message = _("不能删除这条记录")
