# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from rest_framework.response import Response
from pandora.core.code import RETURN_MSG
from rest_framework.renderers import JSONRenderer
from django.utils.encoding import iri_to_uri
from urllib.parse import urlparse
from django.core.exceptions import DisallowedRedirect


class BaseResponse(Response):
    def __init__(self, data=None, status=None, headers=None):
        super(BaseResponse, self).__init__(data, status, headers=headers)


class APIResponse(BaseResponse):
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
        self.data = extra_data

    def json_render(self):
        if not self._is_rendered:
            self.content = JSONRenderer().render(data=self.data)
        return self


class APIOResponseRedirect(BaseResponse):
    """
    An HTTP 302 redirect with an explicit list of allowed schemes.
    Works like django.http.HttpResponseRedirect but we customize it
    to give us more flexibility on allowed scheme validation.
    """
    status_code = 302

    def __init__(self, redirect_to, allowed_schemes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["Location"] = iri_to_uri(redirect_to)
        self.allowed_schemes = allowed_schemes
        self.validate_redirect(redirect_to)

    @property
    def url(self):
        return self["Location"]

    def validate_redirect(self, redirect_to):
        parsed = urlparse(str(redirect_to))
        if not parsed.scheme:
            raise DisallowedRedirect("OAuth2 redirects require a URI scheme.")
        if parsed.scheme not in self.allowed_schemes:
            raise DisallowedRedirect(
                "Redirect to scheme {!r} is not permitted".format(parsed.scheme)
            )
