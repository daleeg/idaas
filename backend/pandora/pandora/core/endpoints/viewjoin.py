# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.urls import path
from rest_framework import exceptions
from django.views.decorators.csrf import csrf_exempt

import logging

LOG = logging.getLogger(__name__)


def join_path(route, views, kwargs=None, name=None):
    view_join = ViewJoin()
    for view in views:
        view_join.register(view)

    return path(route, view_join, kwargs, name)


class ViewJoinReject(Exception):
    pass


class ViewJoin(object):
    def __init__(self):
        self._registry = {}
        self.action_map = {}
        self.actions = self.action_map
        self.csrf_exempt = True

    def register(self, view):
        actions = getattr(view, "actions", None)
        for method, action in actions.items():
            if method in self._registry:
                raise ViewJoinReject("double register:{}-{}".format(method, action))
            self._registry[method] = view
            self.action_map[method] = action

    def view(self, request, *args, **kwargs):
        method = request.method.lower()
        handler_view = self.handler_view(method)
        if not handler_view:
            raise exceptions.MethodNotAllowed(method)

        return handler_view(request, *args, **kwargs)

    def handler_view(self, method):
        return self._registry.get(method)

    def __call__(self, request, *args, **kwargs):
        return self.view(request, *args, **kwargs)
