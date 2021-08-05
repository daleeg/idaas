# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from pandora.models import Token
from pandora.api.serializers import UserAtomSerializer
from django.utils.translation import gettext_lazy as _


class AuditTokenListSerializer(serializers.ModelSerializer):
    last_login_time = serializers.DateTimeField(source="create_time")
    user = UserAtomSerializer()

    class Meta:
        model = Token
        fields = ["uid", "user", "browser", "remote_ip", "platform", "create_time", "last_login_time"]


class AuditTokenRevokeFormSerializer(serializers.Serializer):
    token = serializers.ListSerializer(child=serializers.CharField(), help_text=_("token列表, uid"), )
