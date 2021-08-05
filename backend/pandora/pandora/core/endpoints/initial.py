# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.utils.translation import ugettext_lazy as _
from pandora.business.base import get_object_info
from pandora.core.exceptions import BaseException as BaseAPIException
from pandora.core.exceptions import NoCompanyPermissionDenied
from pandora.core.code import BAD_REQUEST
from django.utils.functional import cached_property
import logging

LOG = logging.getLogger(__name__)


class InitialView(object):
    no_company = False
    company_invade_filter = True
    company_invade_data = True
    path_objects = None

    def check_company(self, request):
        if self.company_is_required and not request.company:
            message = "未查询到公司" if getattr(request, "_error_company", False) else None
            raise NoCompanyPermissionDenied(message)
        self.check_company_permission(request)

    def check_company_permission(self, request):
        pass

    def check_path(self, request, *args, **kwargs):
        for model, lookup_url, lookup_field in self.get_path_objects:
            if not get_object_info(model, kwargs[lookup_url], lookup_field):
                raise BaseAPIException(code=BAD_REQUEST, message=_("没查询到{}".format(lookup_url)))

    @cached_property
    def get_path_objects(self):
        path_objects = []
        if self.path_objects:
            for item in self.path_objects:
                if len(item) == 2:
                    path_objects.append((item[0], item[1], "uid"))
                else:
                    path_objects.append(item)
        return path_objects

    @property
    def company_is_required(self):
        return not self.no_company

    @property
    def company_invade_filter_is_required(self):
        return self.company_invade_filter

    @property
    def company_invade_data_is_required(self):
        return self.company_invade_data

    @property
    def company_id(self):
        return "{}".format(self.company.uid) if self.company else None

    @property
    def company(self):
        return self.request.company
