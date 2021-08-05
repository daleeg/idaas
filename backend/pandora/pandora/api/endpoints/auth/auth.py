# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from pandora.utils.decorators import action
from rest_framework.permissions import IsAuthenticated
from pandora.models import Token
from pandora.core.endpoints.view import AuthBaseEndpoint, NoAuthBaseEndpoint
from pandora.core.response import APIResponse
from pandora.utils.typeutils import errors2string
from pandora.api.serializers.auth import LoginUserSerializer
from pandora.core.code import BAD_REQUEST
from pandora.utils.cacheutils import delete_expire_token, set_expire_token
from pandora.business.auth import get_remote_ip, get_user_agent_info
from pandora.core.code import AUTHENTICATION_FAILED

User = get_user_model()

LOG = logging.getLogger(__name__)

EXPIRE_MINUTES = getattr(settings, "REST_FRAMEWORK_TOKEN_EXPIRE_MINUTES", 60)


class AuthLogoutEndpoint(AuthBaseEndpoint):
    permission_classes = (IsAuthenticated,)

    @action(methods=["post"], detail=False, url_path="logout", url_name="logout")
    def logout(self, request, *args, **kwargs):
        """
        退出(Session)
        """
        tokens = Token.objects.filter(user=request.user)
        for token in tokens:
            delete_expire_token(token.key)
            token.delete()
        return APIResponse()
