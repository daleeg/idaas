# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from rest_framework.response import Response
from pandora.core.code import RETURN_MSG


class APIResponse(Response):
    def __init__(self, data=None, status=200, code=0, message=None, headers=None):
        super(APIResponse, self).__init__(status=status, headers=headers)

        extra_data = {
            'code': code,
            'message': message or RETURN_MSG[code],
            'data': {}
        }
        if data is not None:
            extra_data['data'] = data
        self.code = code
        self.headers = headers
        self.data = extra_data
