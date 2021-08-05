# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.db.models import Q
from pandora.core.endpoints import viewset
from pandora.api import serializers
from pandora.models import Token, UserRoleSet
from pandora.core.schema import RemoveResponseSerializer
from pandora.core.response import APIResponse
from pandora.core.schema import default_parameters
from pandora.utils.decorators import action, swagger_auto_schema
from pandora.utils.cacheutils import delete_expire_token
from pandora.core.code import BAD_REQUEST


class AuditTokenListViewSet(viewset.APIListModelViewSet):
    """
    获取会话令牌列表
    """
    queryset = Token.objects.all()
    serializer_class = serializers.AuditTokenListSerializer
    search_fields = ("user__name", "user__phone", "user__username")
    company_invade_filter = False
    company_invade_data = False


class AuditTokenRevokeViewSet(viewset.GenericViewSet):
    queryset = Token.objects.all()
    serializer_class = serializers.AuditTokenListSerializer
    response_serializer_class = RemoveResponseSerializer
    manual_response_action = ["revoke"]
    company_invade_filter = False
    company_invade_data = False

    @swagger_auto_schema(manual_parameters=default_parameters,
                         request_body=serializers.AuditTokenRevokeFormSerializer)
    @action(methods=["post"], detail=False, url_path="revoke", url_name="revoke")
    def revoke(self, request, *args, **kwargs):
        """
        批量注销令牌
        """

        data = request.data
        tokens = data.get("token", [])
        dest_tokens = Token.objects.filter(uid__in=tokens, )
        dest_tokens_ids = [a.uid for a in dest_tokens]

        if len(tokens) != len(dest_tokens_ids):
            return APIResponse(code=BAD_REQUEST, message=_("存在无效令牌"))

        with transaction.atomic():
            deleted = 0
            for token in dest_tokens:
                delete_expire_token(token.key)
                token.delete(soft=False)
                deleted += 1

        return APIResponse(data={
            "remove": deleted
        })
