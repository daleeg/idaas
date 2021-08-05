# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from pandora.core.code import AUTHENTICATION_FAILED
from django.utils.translation import ugettext_lazy as _
from rest_framework.renderers import JSONRenderer
from pandora.core.header import get_company_header, get_project_label_header
from django.utils.functional import SimpleLazyObject
from pandora.business.company import get_company_object
import logging

LOG = logging.getLogger(__name__)


def get_company(request):
    company_id = get_company_header(request).decode()
    company = None
    if company_id:
        company = get_company_object(company_id)
    return company, True if company_id else False


class CompanyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            request.company = SimpleLazyObject(lambda: self._get_company(request))
            if request.company:
                request.company_id = request.company.uid
            else:
                request.company_id = None
        except Exception as e:
            LOG.error(e)
            ret = {
                "code": AUTHENTICATION_FAILED,
                "message": _("获取公司信息失败")
            }
            return HttpResponse(JSONRenderer().render(data=ret), content_type="application/json")

    def _get_company(self, request):
        if not hasattr(request, "_cached_company"):
            request._cached_company, request._error_company = get_company(request)
        return request._cached_company
