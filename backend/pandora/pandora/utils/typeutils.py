# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.utils.translation import ugettext_lazy as _
from rest_framework.utils.serializer_helpers import ReturnDict

LOG = logging.getLogger(__name__)


def is_child(obj, cls):
    # if not obj or not cls:
    #     return False
    # return _is_child(obj, cls)
    return issubclass(obj, cls)


def _is_child(obj, cls):
    try:
        for i in obj.__bases__:
            if i is cls or isinstance(i, cls):
                return True
        for i in obj.__bases__:
            if is_child(i, cls):
                return True
    except AttributeError:
        return is_child(obj.__class__, cls)
    return False


def errors2string(attrs):
    """
    Convert a dict to string.
    [Note]
    when the dict has many items, return the first item.
    """
    field_message = _('输入信息有误。 错误原因: {msg}')
    non_field_message = _('错误: {msg}')

    if attrs is None:
        return ''
    elif isinstance(attrs, str):
        return attrs
    elif isinstance(attrs, (ReturnDict, dict)):
        for key, msg in attrs.items():
            if isinstance(msg, list):
                msg = ','.join(map(str, msg))
            if key == 'non_field_errors':
                return non_field_message.format(msg=msg)
            LOG.info('Key: {}, Msg:{}'.format(key, msg))
            return field_message.format(msg=msg)
    else:
        return _('错误请求。')


def serrors2string(attrs):
    if attrs is None:
        return ''
    elif isinstance(attrs, str):
        return attrs
    elif isinstance(attrs, (ReturnDict, dict)):
        messages = []
        for key, msg in attrs.items():
            if isinstance(msg, list):
                msg = ','.join(map(str, msg))
            messages.append(msg)
        return ",".join(messages)
    else:
        return ''
