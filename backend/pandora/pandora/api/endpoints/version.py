# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from pandora.core.endpoints.view import NoAuthBaseEndpoint
from pandora.core.response import APIResponse


class VersionEndpoint(NoAuthBaseEndpoint):
    no_company = True
    action_map = {
        "get": "retrieve"
    }

    def get(self, request, *args, **kwargs):
        """
          获取API版本
        """
        print(request.META.get("HTTP_USER_AGENT"))
        version = {
            "inside_version": "v1",
            "detail_version": "V1.11.11",
            "release_version": "E1",
            "version_tag": "IDAAS"
        }
        return APIResponse(version)
