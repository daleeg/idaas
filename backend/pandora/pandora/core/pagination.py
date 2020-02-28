from collections import OrderedDict

from django.core.paginator import InvalidPage
from django.utils import six
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
    def paginate_queryset(self, queryset, request, view=None):
        page_size = self.get_page_size(request)
        if not page_size:
            return None
        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages
        if int(page_number) > paginator.num_pages:
            page_number = paginator.num_pages
        if int(page_number) < 1:
            page_number = 1
        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=six.text_type(exc)
            )
            raise NotFound(msg)
        if paginator.num_pages > 1 and self.template is not None:
            self.display_page_controls = True
        self.request = request
        return list(self.page)


class APIPageNumberPagination(BasePageNumberPagination):
    page_query_param = 'page'
    page_query_description = _('页码')

    page_size_query_param = 'page_size'
    page_size_query_description = _('分页大小')

    def get_paginated_response(self, data):
        return APIResponse(data=(OrderedDict([
            ('count', self.page.paginator.count),
            ('pages', {'page': self.page.number,
                       'page_size': self.get_page_size(self.request)}),
            ('results', data)
        ])))
