# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django.contrib.auth import get_user_model

from rest_framework.serializers import ModelSerializer, CharField

User = get_user_model()

LOG = logging.getLogger(__name__)


class LoginUserSerializer(ModelSerializer):
    token = CharField(read_only=True)

    class Meta:
        model = User
        fields = ("uid", "name", "username", "role", "avatar", "token")
