# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import copy
import re
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.utils.representation import smart_repr
from rest_framework.validators import UniqueTogetherValidator, qs_exists

User = get_user_model()
LOG = logging.getLogger(__name__)


class UsernameValidator(object):
    """
    Validator that corresponds to `validators = [MACFormatValidator(...), ]` on a serializer class.

    Should be applied to an individual field on the serializer.Teacher
    """
    message = _("This field must be unique.")

    def __init__(self, field, message=None):
        self.field = field
        self.serializer_field = None
        self.message = message or self.message

    def __call__(self, attrs):
        value = attrs.get(self.field)
        if value:
            raise ValidationError({self.field: self.message})

    def __repr__(self):
        return "<%s(field=%s)>" % (
            self.__class__.__name__,
            smart_repr(self.field)
        )


class SupperUniqueValidator(UniqueTogetherValidator):
    def __init__(self, queryset, fields, null_fields=None, message=None, exclude_null_fields=None):
        self.queryset = queryset
        self.fields_message = fields
        fields = [key for key in fields.keys()]
        self.null_fields = [] if not null_fields else null_fields
        self.serializer_field = None
        self.message = message or self.message
        self.exclude_null_fields = [] if not exclude_null_fields else exclude_null_fields
        self.null_pass = False
        super(SupperUniqueValidator, self).__init__(queryset=queryset, fields=fields, message=message)

    def enforce_required_fields(self, attrs, serializer):
        """
        The `UniqueTogetherValidator` always forces an implied "required"
        state on the fields it applies to.
        数据唯一性验证处理，请求数据中没有验证字段就不验证，eg:校园视频中没有owner，则不验证owner
        保证验证name和category，有owner则加owner一样验证
        """

        if serializer.instance is not None:
            return

        # missing_items = {
        #     field_name: self.missing_message
        #     for field_name in self.fields
        #     if serializer.fields[field_name].source not in attrs
        # }
        # if missing_items:
        #     raise ValidationError(missing_items, code="required")
        #

        if serializer.instance is not None:
            for field_name in self.fields:
                if field_name not in attrs:
                    attrs[field_name] = getattr(serializer.instance, field_name)
                if attrs[field_name] in [None, ""] and field_name in self.exclude_null_fields:
                    self.null_pass = True
        else:
            for field_name in self.fields:

                if attrs.get(field_name) in [None, ""]:
                    if field_name in self.null_fields:
                        if field_name not in attrs:
                            attrs[field_name] = None
                    elif field_name in self.exclude_null_fields:
                        self.null_pass = True
                    else:
                        raise ValidationError("{}参数不能为空".format(self.fields_message.get(field_name)), code="required")

    def __call__(self, attrs, serializer):

        new_attrs = copy.deepcopy(attrs)
        self.enforce_required_fields(attrs, serializer)
        if self.null_pass:
            return
        queryset = self.queryset
        queryset = self.filter_queryset(new_attrs, queryset, serializer)
        queryset = self.exclude_current_instance(new_attrs, queryset, serializer.instance)

        # Ignore validation if any field is None
        checked_values = [
            value for field, value in attrs.items() if field in self.fields
        ]
        if None not in checked_values and qs_exists(queryset):
            fields = []
            for key, value in self.fields_message.items():
                fields.append("{}={}".format(value, new_attrs.get(key)))
            field_names = ", ".join(fields)
            message = self.message.format(field_names=field_names)
            raise ValidationError(message, code="unique")


def validate_email_domain(value):
    if not value or "@" not in value:
        return False

    user_part, domain_part = value.rsplit("@", 1)
    domain_regex = re.compile(
        # max length for domain name labels is 63 characters per RFC 1034
        r"((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+)(?:[A-Z0-9-]{2,63}(?<!-))\Z",
        re.IGNORECASE)
    if domain_regex.match(domain_part):
        return True
    else:
        return False


class EmailValidator(object):
    message = _("邮箱设定不合法, 请确认是否填写正确.")

    def __init__(self, email_field, message=None):
        self.email_field = email_field
        self.message = message or self.message

    def set_context(self, serializer):
        """
        This hook is called by the serializer instance,
        prior to the validation call being made.
        """
        # Determine the existing instance, if this is an update operation.
        self.instance = getattr(serializer, "instance", None)

    def __call__(self, attrs, serializer):
        email_field = attrs.get(self.email_field)
        if email_field and not validate_email_domain(email_field):
            raise ValidationError({"email": self.message})
