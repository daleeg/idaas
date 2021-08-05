# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

from pandora.api.serializers import CompanySerializer, CompanyListSerializer
from pandora.models import Company

from pandora.core.endpoints.viewset import APIModelViewSet, APIListModelViewSet


LOG = logging.getLogger(__name__)


class CompanyViewSet(APIModelViewSet):
    """
    create:
        创建公司
    bulk_create:
        批量创建公司
    list:
        查询公司列表
    bulk_destroy:
        批量删除公司
    destroy:
        删除公司
    update:
        修改公司
    retrieve:
        获取公司详情
    micro_list:
        获取公司最小化列表
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    serializer_micro_class = CompanyListSerializer
    lookup_url_kwarg = "company_id"
    filter_fields = ("name",)
    search_fields = ("name",)
    no_company = True
    company_invade_filter = False
    company_invade_data = False
