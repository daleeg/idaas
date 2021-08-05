# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from pandora.core.response import APIResponse
from pandora.core.endpoints.generic import GenericViewSet
from pandora.core.endpoints.mixins import CreateModelMixin, UpdateModelMixin, BulkCreateModelMixin
from pandora.core.endpoints.mixins import RetrieveModelMixin, ListModelMixin
from pandora.core.endpoints.mixins import BulkDestroyModelMixin, DestroyModelMixin
from pandora.core.endpoints.mixins import DownloadExcelModelMixin, UploadExcelModelMixin

LOG = logging.getLogger(__name__)


class APIModelViewSet(CreateModelMixin,
                      RetrieveModelMixin,
                      UpdateModelMixin,
                      ListModelMixin,
                      DestroyModelMixin,
                      BulkDestroyModelMixin,
                      BulkCreateModelMixin,
                      GenericViewSet
                      ):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    lookup_field = "uid"


class APIListModelViewSet(ListModelMixin,
                          GenericViewSet):
    """
    A viewset that provides default `list()`  actions.
    """
    pass


class APIInfoModelViewSet(ListModelMixin,
                          GenericViewSet):
    """
    A viewset that provides default `list()`  actions.
    """
    pagination_class = ()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.get_distinct():
            queryset = queryset.distinct()
        if self.order_by_fields and isinstance(self.order_by_fields, tuple):
            queryset = queryset.order_by(*self.order_by_fields)
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(self.final_response_data(serializer.data))
        if queryset:
            instance = queryset[0]
            serializer = self.get_serializer(instance)
            data = [serializer.data]
        else:
            data = None
        return APIResponse(data=self.final_response_data(data))

    def final_response_data(self, data):
        if data:
            return {"results": data[0]}
        return {"results": None}


class APICreateModelViewSet(CreateModelMixin, GenericViewSet):
    """
    A viewset that provides default `create()` actions.
    """
    pass


class APIUpdateModelViewSet(UpdateModelMixin, GenericViewSet):
    """
    A viewset that provides default `update()` and `partial_update()` actions.
    """
    pass


class APIListUpdateModelViewSet(ListModelMixin, UpdateModelMixin, GenericViewSet):
    """
    A viewset that provides default `list()` and `update()` actions.
    """
    pass


class APIUpdateRetrieveDeleteModelViewSet(RetrieveModelMixin,
                                          UpdateModelMixin,
                                          DestroyModelMixin, GenericViewSet):
    """
    A viewset that provides default `update()` , `retrieve()`,`partial_update()` and `destroy()`actions.
    """
    pass


class APIUpdateRetrieveModelViewSet(RetrieveModelMixin,
                                    UpdateModelMixin,
                                    GenericViewSet):
    """
    A viewset that provides default `update()` , `retrieve()`,`partial_update()` and `destroy()`actions.
    """
    pass


class APIRetrieveModelViewSet(RetrieveModelMixin, GenericViewSet):
    """
    A viewset that provides default `retrieve()` actions.
    """
    pass


class APIListDeleteBatModelViewSet(ListModelMixin, DestroyModelMixin,
                                   BulkDestroyModelMixin, GenericViewSet):
    """
    A viewset that provides default `list()` and `retrieve()` actions.
    """
    pass


class APICreateUpdateDeleteBatModelViewSet(CreateModelMixin, UpdateModelMixin, BulkDestroyModelMixin,
                                           DestroyModelMixin, GenericViewSet):
    pass


class APIDownloadExcelModelViewSet(DownloadExcelModelMixin, GenericViewSet):
    """
    A viewset that provides default `download()` actions.
    """
    pass


class APIUploadExcelModelViewSet(UploadExcelModelMixin, GenericViewSet):
    """
    A viewset that provides default `upload()` actions.
    """
    pass


class APIModelGenericViewSet(CreateModelMixin,
                             RetrieveModelMixin,
                             UpdateModelMixin,
                             ListModelMixin,
                             DestroyModelMixin,
                             GenericViewSet
                             ):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    lookup_field = "uid"


class APIListCreateUpdateDeleteModelViewSet(CreateModelMixin, UpdateModelMixin, ListModelMixin, DestroyModelMixin,
                                            GenericViewSet):
    """
    A viewset that provides default `create()`, `list()`, `update()`,
     `destroy()` actions.
    """
    lookup_field = "uid"


class APIListCreateDeleteModelViewSet(CreateModelMixin, UpdateModelMixin, ListModelMixin,  DestroyModelMixin,
                                      GenericViewSet):
    """
    A viewset that provides default `create()`, `list()`, `destroy()` actions.
    """
    lookup_field = "uid"


class APIListCreateModelViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    """
    A viewset that provides default `list()` and `create()` actions.
    """
    pass


class APIListRetrieveModelViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    A viewset that provides default `list()` and `Retrieve()` actions.
    """
    pass
