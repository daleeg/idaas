# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from rest_framework.permissions import IsAuthenticated
from pandora.core.permissions import ActivePermission
from pandora.core.endpoints.generic import APIGenericView
from pandora.core.endpoints import mixins

import logging

LOG = logging.getLogger(__name__)


class APICreateModelView(mixins.CreateModelMixin,
                         APIGenericView):
    """
    Concrete view for creating a model instance.
    """

    action_map = {
        "post": "create"
    }

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class APIBulkCreateModelView(mixins.BulkCreateModelMixin,
                             APIGenericView):
    """
    Concrete view for creating a model instance.
    """

    action_map = {
        "post": "bulk_create"
    }

    def post(self, request, *args, **kwargs):
        return self.bulk_create(request, *args, **kwargs)


class APIListModelView(mixins.ListModelMixin,
                       APIGenericView):
    """
    Concrete view for listing a queryset.
    """
    action_map = {
        "get": "list"
    }

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class APIRetrieveModelView(mixins.RetrieveModelMixin,
                           APIGenericView):
    """
    Concrete view for retrieving a model instance.
    """
    action_map = {
        "get": "retrieve"
    }

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class APIDestroyModelView(mixins.DestroyModelMixin,
                          APIGenericView):
    """
    Concrete view for deleting a model instance.
    """
    action_map = {
        "delete": "destroy"
    }

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class APIBulkDestroyModelView(mixins.BulkDestroyModelMixin,
                              APIGenericView):
    """
    Concrete view for deleting a model instance.
    """
    action_map = {
        "post": "bulk_destroy"
    }

    def post(self, request, *args, **kwargs):
        return self.bulk_destroy(request, *args, **kwargs)


class APIUpdateModelView(mixins.UpdateModelMixin,
                         APIGenericView):
    """
    Concrete view for updating a model instance.
    """

    action_map = {
        "put": "update"
    }

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    # def patch(self, request, *args, **kwargs):
    #     return self.partial_update(request, *args, **kwargs)


class APIListCreateModelView(mixins.ListModelMixin,
                             mixins.CreateModelMixin,
                             APIGenericView):
    """
    Concrete view for listing a queryset or creating a model instance.
    """

    action_map = {
        "get": "list",
        "post": "create"
    }

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class APIRetrieveUpdateModelView(mixins.RetrieveModelMixin,
                                 mixins.UpdateModelMixin,
                                 APIGenericView):
    """
    Concrete view for retrieving, updating a model instance.
    """

    action_map = {
        "get": "retrieve",
        "put": "update"
    }

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    # def patch(self, request, *args, **kwargs):
    #     return self.partial_update(request, *args, **kwargs)


class APIRetrieveDestroyModelView(mixins.RetrieveModelMixin,
                                  mixins.DestroyModelMixin,
                                  APIGenericView):
    """
    Concrete view for retrieving or deleting a model instance.
    """
    action_map = {
        "delete": "destroy",
        "get": "retrieve"
    }

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class APIRetrieveUpdateDestroyModelView(mixins.RetrieveModelMixin,
                                        mixins.UpdateModelMixin,
                                        mixins.DestroyModelMixin,
                                        APIGenericView):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """
    action_map = {
        "delete": "destroy",
        "get": "retrieve",
        "put": "update",
    }

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    # def patch(self, request, *args, **kwargs):
    #     return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class AuthBaseEndpoint(APIGenericView):
    pagination_class = None
    permission_classes = (ActivePermission, IsAuthenticated)


class NoAuthBaseEndpoint(APIGenericView):
    pagination_class = None
    authentication_classes = ()
    permission_classes = ()
