from collections import OrderedDict

from django.core.paginator import InvalidPage
from django.utils.translation import ugettext_lazy as _
from rest_framework import pagination
from rest_framework.exceptions import NotFound

from pandora.core.response import APIResponse


class APIPagination(pagination.LimitOffsetPagination):
    def get_paginated_response(self, data):
        return APIResponse(data=OrderedDict([
            ('count', self.count),
            ('links', {'next': self.get_next_link(),
                       'previous': self.get_previous_link()}),
            ('results', data)
        ]))


class BasePageNumberPagination(pagination.PageNumberPagination):
    def __init__(self):
        super(BasePageNumberPagination, self).__init__()
        self.total = 0

    def get_count(self, queryset):
        """
        Determine an object count, supporting either querysets or regular lists.
        """
        try:
            return queryset.count()
        except (AttributeError, TypeError):
            return len(queryset)

    def get_page_size(self, request):
        page_size = super(BasePageNumberPagination, self).get_page_size(request)
        page_size = page_size or self.total
        return page_size

    def paginate_queryset(self, queryset, request, view=None):
        self.total = self.get_total(queryset)
        return super(BasePageNumberPagination, self).paginate_queryset(queryset, request, view)

    def get_page_number(self, request, paginator):
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings or int(page_number) > paginator.num_pages:
            page_number = paginator.num_pages
        if int(page_number) < 1:
            page_number = 1
        return page_number


class APIPageNumberPagination(BasePageNumberPagination):
    page_query_param = 'page'
    page_query_description = _('页码')

    page_size_query_param = 'page_size'
    page_size_query_description = _('分页大小')

    def get_paginated_response(self, data):
        return APIResponse(data=(OrderedDict([
            ('count', self.page.paginator.count),
            ('total', self.total),
            ('pages', {'page': self.page.number,
                       'page_size': self.get_page_size(self.request)}),
            ('results', data)
        ])))
