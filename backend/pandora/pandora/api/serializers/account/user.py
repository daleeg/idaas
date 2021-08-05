# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
User = get_user_model()

__all__ = [
    "UserPasswordReqSerializer",
    "UserEmailReqSerializer",
    "UserPhoneReqSerializer",

]

LOG = logging.getLogger(__name__)


class UserPasswordReqSerializer(serializers.Serializer):
    password = serializers.CharField(help_text=_("密码,base64"))
    confirm_password = serializers.CharField(help_text=_("确认密码,base64"))


class UserEmailReqSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text=_("邮箱"))


class UserPhoneReqSerializer(serializers.Serializer):
    phone = serializers.CharField(help_text=_("电话"))

