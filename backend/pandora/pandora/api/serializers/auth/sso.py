# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django.contrib.auth import get_user_model

from rest_framework.serializers import ModelSerializer


User = get_user_model()

LOG = logging.getLogger(__name__)


class SsoLoginUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("uid", "name", "username", "role", "avatar",)
