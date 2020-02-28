# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.authtoken.models import Token
from django.conf import settings
import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from pandora.core.exceptions import AuthenticationFailed
from pandora.core.user import DeviceUser, VirthSuperUser
from pandora.utils.cacheutils import get_sn_token, set_sn_token, get_expire_token, set_expire_token, delete_expire_token

EXPIRE_MINUTES = getattr(settings, 'REST_FRAMEWORK_TOKEN_EXPIRE_MINUTES', 60)


class SessionAuthentication(BaseAuthentication):
    """
    Use Django's session framework for authentication.
    """

    def authenticate(self, request):
        """
        Returns a `User` if the request session currently has a logged in user.
        Otherwise returns `None`.
        """

        # Get the session-based user from the underlying HttpRequest object
        user = getattr(request._request, 'user', None)

        # CSRF validation not required
        if not user or not user.is_active:
            return None

        return user, None


class TokenAuthentication(BaseAuthentication):
    """
    Simple token based authentication

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """
    model = Token

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'token':
            return None

        if len(auth) == 1:
            raise AuthenticationFailed(_("没有提供认证信息（认证令牌HTTP头无效）。"))
        elif len(auth) > 2:
            raise AuthenticationFailed(_("认证令牌字符串不应该包含空格（无效的认证令牌HTTP头）。"))

        try:
            token = auth[1].decode()
        except UnicodeError:
            raise AuthenticationFailed(_("无效的Token。Token字符串不能包含非法的字符。"))

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.select_related('user').get(key=key)
        except self.model.DoesNotExist:
            raise AuthenticationFailed(_("认证令牌无效。"))

        if not token.user.is_active:
            raise AuthenticationFailed(_("用户未激活或者已删除。"))

        return token.user, token

    def authenticate_header(self, request):
        return 'Token'


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        # Search token in cache
        cache_user_token = get_expire_token(key)
        if cache_user_token:
            set_expire_token(key, cache_user_token)
            return cache_user_token

        model = self.model
        try:
            token = model.objects.select_related('user').get(key=key)
        except (model.DoesNotExist, model.MultipleObjectsReturned):
            raise AuthenticationFailed(_('登录已失效, 请重新登录'))

        if not token.user.is_active:
            raise AuthenticationFailed(_('用户未激活或者已删除.'))

        time_now = timezone.now()

        if token.created < time_now - datetime.timedelta(minutes=EXPIRE_MINUTES):
            delete_expire_token(key)
            token.delete()
            raise AuthenticationFailed(_('登录已超时，请重新登录'))

        if token:
            # Cache token
            set_expire_token(key, (token.user, token))

        return token.user, token


class SkeletonKeyAuthentication(BaseAuthentication):
    """
    Simple sn based authentication

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "SkeletonKey".  For example:

        Authorization: Skeleton aaaa bbbb
    """

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'skeleton':
            return None

        elif len(auth) != 3:
            raise AuthenticationFailed(_("认证令牌字符串格式不正确"))

        try:
            client_id = auth[1].decode()
            client_secret = auth[2].decode()
        except UnicodeError:
            raise AuthenticationFailed(_("无效的SkeletonKey, 字符串不能包含非法的字符。"))

        user = VirthSuperUser(client_id)
        if not user.check_password(client_secret):
            raise AuthenticationFailed(_("无效的SkeletonKey, secret和id不匹配"))
        return user, client_secret
