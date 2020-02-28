# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import copy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.utils.representation import smart_repr
from rest_framework.validators import UniqueTogetherValidator, qs_exists
from pandora import models

User = get_user_model()
LOG = logging.getLogger(__name__)


class UsernameValidator(object):
    """
    Validator that corresponds to `validators = [MACFormatValidator(...), ]` on a serializer class.

    Should be applied to an individual field on the serializer.
    """
    message = _('This field must be unique.')

    def __init__(self, field, message=None):
        self.field = field
        self.serializer_field = None
        self.message = message or self.message

    def __call__(self, attrs):
        value = attrs.get(self.field)
        if value:
            raise ValidationError({self.field: self.message})

    def __repr__(self):
        return '<%s(field=%s)>' % (
            self.__class__.__name__,
            smart_repr(self.field)
        )


class NumberValidator(object):
    """
    Validator that corresponds to `validators = [MACFormatValidator(...), ]` on a serializer class.

    Should be applied to an individual field on the serializer.
    """
    message = 'This field {} must be unique, and not same with username, email, phone, number.'

    def __init__(self, fields, message=None):
        self.fields = fields
        self.message = message or self.message

    def __call__(self, attrs):
        for field in self.fields:
            value = attrs.get(field)
            if value:
                user = attrs.get("user", None)
                if user:
                    users = User.objects.exclude(uid=user.uid).filter(Q(username=value) | Q(email=value))
                    teachers = models.Teacher.objects.filter(Q(phone=value) | Q(number=value))
                    admins = models.Admin.objects.filter(Q(phone=value) | Q(number=value))
                    students = models.Student.objects.filter(Q(phone=value) | Q(number=value))
                    if users.exists() or teachers.exists() or admins.exists() or students.exists():
                        raise ValidationError({field: _(self.message.format(field))})

    def __repr__(self):
        return '<%s(field=%s)>' % (
            self.__class__.__name__,
            smart_repr(self.field)
        )


class NirvanaValidator(UniqueTogetherValidator):
    def __init__(self, queryset, fields, null_fields=None, message=None, exclude_null_fields=None):
        self.queryset = queryset
        self.fields_message = fields
        fields = [key for key in fields.keys()]
        self.null_fields = [] if not null_fields else null_fields
        self.serializer_field = None
        self.message = message or self.message
        self.exclude_null_fields = [] if not exclude_null_fields else exclude_null_fields
        self.null_pass = False
        super(NirvanaValidator, self).__init__(queryset=queryset, fields=fields, message=message)

    def enforce_required_fields(self, attrs):
        """
        The `UniqueTogetherValidator` always forces an implied 'required'
        state on the fields it applies to.
        数据唯一性验证处理，请求数据中没有验证字段就不验证，eg:校园视频中没有owner，则不验证owner
        保证验证name和category，有owner则加owner一样验证
        """
        if self.instance is not None:
            for field_name in self.fields:
                if field_name not in attrs:
                    attrs[field_name] = getattr(self.instance, field_name)
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
                        raise ValidationError("{}参数不能为空".format(self.fields_message.get(field_name)), code='required')

    def __call__(self, attrs):
        new_attrs = copy.deepcopy(attrs)
        self.enforce_required_fields(new_attrs)

        if self.null_pass:
            return

        queryset = self.queryset
        queryset = self.filter_queryset(new_attrs, queryset)
        queryset = self.exclude_current_instance(new_attrs, queryset)

        if qs_exists(queryset):
            fields = []
            for key, value in self.fields_message.items():
                fields.append("{}={}".format(value, new_attrs.get(key)))
            field_names = ', '.join(fields)
            message = self.message.format(field_names=field_names)
            raise ValidationError(message, code='unique')
