# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from rest_framework import status
from rest_framework.views import APIView
from pandora.core.response import APIResponse
import pandora.core.schema as ms

import logging

LOG = logging.getLogger(__name__)


class BaseEndpoint(APIView):
    permission_classes = ()
    schema = ms.ManualViewSchema()

    def options(self, request, *args, **kwargs):
        """
        Handler method for HTTP 'OPTIONS' request.
        """
        if self.metadata_class is None:
            return self.http_method_not_allowed(request, *args, **kwargs)
        data = self.metadata_class().determine_metadata(request, self)
        return APIResponse(data, status=status.HTTP_200_OK)


class NoAuthBaseEndpoint(BaseEndpoint):
    authentication_classes = ()
    permission_classes = ()


