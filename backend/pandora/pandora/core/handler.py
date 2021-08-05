from django.core.exceptions import PermissionDenied
from django.http import Http404
import django.core.exceptions as de
from django.db.utils import DataError, DatabaseError
from django.utils import timezone
from django.db.utils import IntegrityError
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.views import set_rollback
import rest_framework.exceptions as rest_exc
from rest_framework.serializers import ValidationError
from pandora.core.response import APIResponse
from pandora.core.code import BAD_REQUEST, NO_PERMISSION, DATA_CONFLICT, DELETE_FORBIDDEN, MYSQL_GONE_AWAY
from pandora.core.code import DATABASE_ERROR
from pandora.core.exceptions import CreateError, FetchError, DeleteError, UpdateError, DataInvalidError, NetworkError
from pandora.core.exceptions import DeleteProtectedError, BaseException, DataException
from pandora.utils.typeutils import errors2string

from rest_framework.authentication import get_authorization_header

import re
import logging
import traceback

LOG = logging.getLogger(__name__)


def exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django"s built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    error_str = traceback.print_exc()
    if error_str:
        LOG.error(error_str)
    if isinstance(exc, BaseException):
        headers = {}
        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header
        if getattr(exc, "wait", None):
            headers["Retry-After"] = "%d" % exc.wait
        code = exc.detail.get("code")
        data = exc.detail.get("data")
        message = exc.detail.get("message")
        set_rollback()
        return APIResponse(code=code, message=message, data=data, status=exc.status_code, headers=headers)

    elif isinstance(exc, rest_exc.APIException):
        headers = {}
        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header
        if getattr(exc, "wait", None):
            headers["Retry-After"] = "%d" % exc.wait

        if isinstance(exc, ValidationError):
            set_rollback()
            return APIResponse(message=errors2string(exc.detail), code=BAD_REQUEST)

        if isinstance(exc.detail, (list, dict)):
            if "code" in exc.detail:
                code = exc.detail.get("code")
                data = exc.detail.get("data")
                message = exc.detail.get("message")
            else:
                code = BAD_REQUEST
                data = None
                message = "{}".format(exc.detail)
        else:
            code = BAD_REQUEST
            data = None
            message = "{}".format(exc.detail)

        set_rollback()
        return APIResponse(code=code, message=message, data=data, status=exc.status_code, headers=headers)
    elif isinstance(exc, Http404):
        msg = _("Not found.")
        set_rollback()
        return APIResponse(message=msg, status=status.HTTP_404_NOT_FOUND, code=BAD_REQUEST)

    elif isinstance(exc, PermissionDenied):
        msg = _("Permission denied.")
        set_rollback()
        return APIResponse(message=msg, status=status.HTTP_403_FORBIDDEN, code=NO_PERMISSION)

    elif isinstance(exc, CreateError):
        msg = _("创建失败, {}".format(exc))
        if "MySQL server has gone away" in str(exc):
            return APIResponse(code=MYSQL_GONE_AWAY)
        set_rollback()
        return APIResponse(message=msg, code=BAD_REQUEST)

    elif isinstance(exc, FetchError):
        msg = _("获取失败, {}".format(exc))
        set_rollback()
        return APIResponse(message=msg, code=BAD_REQUEST)

    elif isinstance(exc, DeleteError):
        msg = _("删除失败, {}".format(exc))
        set_rollback()
        return APIResponse(message=msg, code=BAD_REQUEST)

    elif isinstance(exc, UpdateError):
        msg = _("修改失败, {}".format(exc))
        set_rollback()
        return APIResponse(message=msg, code=BAD_REQUEST)

    elif isinstance(exc, NetworkError):
        msg = _("网络异常, {}".format(exc))
        set_rollback()
        return APIResponse(message=msg, code=BAD_REQUEST)

    elif isinstance(exc, de.ValidationError):
        msg = _("参数错误, {}".format(exc.messages))
        set_rollback()
        return APIResponse(message=msg, code=BAD_REQUEST)

    elif isinstance(exc, AttributeError):
        msg = _("参数错误:{}".format(exc))
        set_rollback()
        return APIResponse(message=msg, code=BAD_REQUEST)

    elif isinstance(exc, ValueError):
        msg = _("Value Error:{}".format(exc))
        set_rollback()
        return APIResponse(message=msg, code=BAD_REQUEST)

    elif isinstance(exc, TimeoutError):
        msg = _("Timeout Error:{}".format(exc))
        set_rollback()
        return APIResponse(message=msg, code=BAD_REQUEST)

    elif isinstance(exc, AssertionError):
        msg = _("AssertionError Error:{}".format(exc))
        set_rollback()
        return APIResponse(message=msg, code=BAD_REQUEST)

    elif isinstance(exc, IntegrityError):
        try:
            pandora_uk_list = str(exc).split(":")[-1].split(",")
            uk_list = list(map(lambda _: _.split(".")[-1], pandora_uk_list))
            if "is_deleted" in uk_list:
                uk_list.remove("is_deleted")
            map_uk_list = list(map(lambda uk: getattr(UniqueKeyMap, uk), uk_list))
            msg = _("该数据无法保存，由于({})产生冲突".format(",".join(map_uk_list)))
        except (Exception,):
            try:
                s1 = str(exc).split(",")[1]
                exc_res = re.search(" \"(?P<name>\w+)-", s1)
                if exc_res:
                    msg = _("数据冲突, 详情:字段[{}]已存在 ".format(exc_res.groupdict()["name"]))
                else:
                    msg = _("数据冲突, 详情:{}".format(exc))
            except (Exception,):
                msg = _("{}".format(table_map.get_chinese(str(exc))))
        set_rollback()
        return APIResponse(message=msg, code=DATA_CONFLICT)

    elif isinstance(exc, DeleteProtectedError):
        msg = exc.message
        set_rollback()
        return APIResponse(message=msg, code=DELETE_FORBIDDEN)

    elif isinstance(exc, DataInvalidError):
        msg = exc.message
        set_rollback()
        return APIResponse(message=msg, code=BAD_REQUEST)

    elif isinstance(exc, DatabaseError):
        if isinstance(exc, DataError):
            exc_res = re.search("Data too long for column \"(?P<name>\w+)\"", "{}".format(exc))
            if exc_res:
                msg = _("数据库字段错误, 详情:字段{}超长 ".format(exc_res.groupdict()["name"]))
            else:
                msg = _("数据库字段错误, 详情:{}".format(exc))
        else:
            if "MySQL server has gone away" in str(exc):
                set_rollback()
                return APIResponse(code=MYSQL_GONE_AWAY)
            msg = _("数据库错误, 详情:{}".format(exc))
        set_rollback()
        return APIResponse(message=msg, code=DATABASE_ERROR)

    # Note: Unhandled exceptions will raise a 500 error.
    return None


class UniqueKeyMap(object):
    name = "名称"
    username = "用户名"
    category = "类型"
    album = "相册"


class TableMap(object):
    defaults = dict(
    )

    def __init__(self, name, **kwargs):
        self._name = name
        self.__dict__.update(self.defaults)
        self._set_kwargs(**kwargs)

    def _set_kwargs(self, **kw):
        for key, value in kw.items():
            self.__dict__[key] = value

    def get_chinese(self, input_str):
        output = input_str
        for table in self.attr_list:
            key = "{}_".format(table)
            if key in input_str:
                output = self.__dict__.get(table)
                break
        output = "{}, 详情: {}.".format(self._name, output)
        return output

    @property
    def attr_list(self):
        key_list = list(self.__dict__.keys())
        key_list.sort()
        key_list.remove("_name")
        return key_list

    def __repr__(self):
        return "<%s `%s`>" % (self.__class__.__name__, self._name)

    def clone(self, name, **kwds):
        r = self.__class__(name)
        r.__dict__ = self.__dict__.copy()
        r._name = name
        r._set_kwargs(**kwds)
        return r


table_map = TableMap(name="数据冲突")


def finalize_response_handler(context, request, response, *args, **kwargs):
    try:
        path = request._request.get_full_path()
        method = request._request.method
        input_data = request.data.copy()
        if "upload" in path:
            input_data.pop("file", None)
        param = "BODY: {}".format(input_data)
        header_auth = "AUTHORIZATION: {}".format(get_authorization_header(request._request))
        body = [" " * 33 + x for x in [header_auth, param]]
        duration = timezone.now().timestamp() - context["view"]._current.timestamp()
        url = "[{}] [{:.4f} s] {}://{}:{}".format(
            method, duration, request._request.scheme, request._request.get_host(), path)
        info = "\n".join([url] + body)
        LOG.info(info)
        # flow_statistic(request)
    except Exception as e:
        LOG.info(e)


def flow_statistic(request, **kwargs):
    pass
