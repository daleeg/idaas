# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from pandora import models
from pandora.core.serializers import serializers


class UserAtomSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ("uid", "name", "avatar", "phone", "email")

