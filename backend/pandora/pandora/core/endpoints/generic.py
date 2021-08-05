# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from inspect import getmembers
from django.utils import timezone
from django.utils.encoding import force_text as _t
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from rest_framework import viewsets as vs
from rest_framework import status
from rest_framework import generics
from rest_framework.reverse import reverse
from rest_framework.serializers import Serializer
from rest_framework.permissions import IsAuthenticated
from pandora.core.handler import finalize_response_handler
from pandora.core.exceptions import NotAuthenticated, PermissionDenied
from pandora.core.permissions import ActivePermission
from pandora.core.response import APIResponse
import pandora.core.schema.manual as ms
from pandora.core.code import NOT_FOUND
from pandora.core.endpoints.initial import InitialView
from pandora.core.collection import ScaleSet
from pandora.core.exceptions import BaseException as BaseAPIException
from rest_framework.decorators import MethodMapper
import logging

LOG = logging.getLogger(__name__)


class GenericAPIView(InitialView, generics.GenericAPIView):
    serializer_class = Serializer
    serializer_details_class = None
    serializer_micro_class = None
    response_serializer_class = None
    serializer_create_class = None
    serializer_update_class = None
    serializer_destroy_class = None
    path_invade_filter_fields = None
    path_invade_data_fields = None
    context = None
    scale_action = ("list", "retrieve")
    manual_response_action = ()
    order_by_fields = ()
    action_map = None
    native_response = False
    auto_audit_log = True  # 是否自动记录操作审计
    model_name = None  # 操作对象名称
    log_body_action = []  # 记录request body的action，全部为__all__
    distinct = False
    permission_classes = (ActivePermission, IsAuthenticated)
    schema = ms.ManualViewSchema(
        all=[
            ms.ManualField(
                name="Authorization",
                location=ms.HEADER,
                schema=ms.STRING(description=_t("自定义token认证, Basic 1234 or Token 1234")),
            ),
            ms.ManualField(
                name=settings.COMPANY_HEADER_LOWER,
                location=ms.HEADER,
                schema=ms.STRING(description=_t("公司标识")),
            ),
        ],

    )

    def initial(self, request, *args, **kwargs):
        setattr(self, "_current", timezone.now())

        if self.company_invade_data_is_required:
            if self.action in ("create", "update"):
                if "company_id" not in request.data:
                    request.data["company_id"] = self.company_id
            elif self.action in ("bulk_create",):
                for item in request.data:
                    if "company_id" not in item:
                        item["company_id"] = self.company_id
        if self.path_invade_data_fields:
            for lookup, lookup_url in self.path_invade_data_fields:
                lookup_data = self.kwargs.get(lookup_url)
                if self.action in ("create", "update"):
                    if lookup not in request.data:
                        request.data[lookup] = lookup_data
                elif self.action in ("bulk_create",):
                    for item in request.data:
                        if lookup not in item:
                            item[lookup] = lookup_data
        if self.path_invade_filter_fields:
            if self.action in ("list", "retrieve", "delete", "bulk_delete", "update"):
                _mutable = self.request.GET._mutable
                self.request.GET._mutable = True
                for lookup, lookup_url in self.path_invade_filter_fields:
                    lookup_data = self.kwargs.get(lookup_url)
                    self.request.GET[lookup] = lookup_data
                self.request.GET._mutable = _mutable

        if self.action in ("list", "retrieve", "delete", "bulk_delete", "update"):
            _mutable = self.request.GET._mutable
            self.request.GET._mutable = True
            filter_kwargs = {k: v for k, v in self.kwargs.items() if
                             k not in ["version", self.lookup_url_kwarg] and k not in self.request.query_params}
            if self.company_invade_filter_is_required and "company_id" not in self.request.query_params:
                filter_kwargs["company_id"] = self.company_id
            self.request.GET.update(filter_kwargs)
            self.request.GET._mutable = _mutable

        super(GenericAPIView, self).initial(request, *args, **kwargs)
        self.check_company(request)
        self.check_path(request, *args, **kwargs)

    def get_response_serializer(self, *args, **kwargs):
        if self.manual_response_action and self.action in self.manual_response_action and self.response_serializer_class:
            kwargs.setdefault("context", self.get_serializer_context())
            return self.response_serializer_class(*args, **kwargs)
        return self.get_serializer(*args, **kwargs)

    @property
    def current(self):
        return getattr(self, "_current", timezone.now())

    def record_audit_log(self, request, response, action=None, model_name=None):
        if not model_name:
            if self.model_name:
                model_name = self.model_name
            elif self.queryset is not None:
                model_name = self.queryset.model.__name__
        # action = action or self.audit_log_action.get(self.action)
        # actor = catch_username(request)
        # if not (action and model_name and actor):
        #     return
        # audit_status = AuditLogStatusSet.FAILED
        # if response.status_code in (200, 201):
        #     if isinstance(response, HttpResponse):
        #         audit_status, message = AuditLogStatusSet.SUCCESS, "success"
        #     else:
        #         if response.data["code"] == 0:
        #             audit_status = AuditLogStatusSet.SUCCESS
        #         message = response.data["message"]
        #     audit_info = {"model_name": model_name, "action": action, "status": audit_status, "message": str(message),
        #                   "actor": actor}
        #     if self.log_body_action == "__all__" or self.action in self.log_body_action:
        #         audit_info["extra"] = request.data
        #     AuditLog.add_audit_log(self.company_id, **audit_info)

    def finalize_response(self, request, response, *args, **kwargs):
        ret = super(GenericAPIView, self).finalize_response(request, response, *args, **kwargs)
        finalize_response_handler(self.get_finalize_context(), request, response, *args, **kwargs)
        if self.auto_audit_log:
            self.record_audit_log(request, response)
        return ret

    def get_finalize_context(self):
        """
        Returns a dict that is passed through to EXCEPTION_HANDLER,
        as the `context` argument.
        """
        return {
            "view": self,
            "args": getattr(self, "args", ()),
            "kwargs": getattr(self, "kwargs", {}),
            "request": getattr(self, "request", None)
        }

    def permission_denied(self, request, message=None, code=None):
        if not request.successful_authenticator:
            raise NotAuthenticated()
        raise PermissionDenied()

    def pre_request_data(self, data):
        if self.action in ("create", "bulk_create"):
            code = data.get("code", None)
            if not code:
                data.pop("code", None)
        return data

    def pre_update_request_data(self, instance, data):
        return self.pre_request_data(data)

    def get_queryset(self):
        queryset = super(GenericAPIView, self).get_queryset()
        if self.action in ("list", "retrieve", "delete", "bulk_delete", "update"):
            if self.company_invade_filter_is_required:
                company_id = self.company_id
                queryset = queryset.filter(company_id=company_id)
            if self.path_invade_filter_fields:
                for lookup, lookup_url in self.path_invade_filter_fields:
                    queryset = queryset.filter(**{lookup: self.kwargs.get(lookup_url)})

        return queryset

    def final_response_data(self, data):
        return data

    def get_context(self):
        context = {} if not self.context else self.context
        assert isinstance(context, dict), (
            '"{}" should include a `context` dict attribute.'.format(self.__class__.__name__)
        )
        self.context = context
        return context

    def set_context(self, **kwargs):
        self.get_context().update(kwargs)

    def filter_queryset(self, queryset):
        """
        Given a queryset, filter it with whichever filter backend is in use.

        You are unlikely to want to override this method, although you may need
        to call it either from a list view, or from a custom `get_object`
        method if you want to apply the configured filtering backend to the
        default queryset.
        """
        filter_backends = list(self.filter_backends)
        for backend in filter_backends:
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get_distinct(self):
        return self.distinct

    def get_serializer_class(self):
        serializer_class = super(GenericAPIView, self).get_serializer_class()
        _scale = self.get_query_scale()
        if _scale == ScaleSet.MICRO:
            serializer_class = self.serializer_micro_class
        elif _scale == ScaleSet.DETAIL:
            serializer_class = self.serializer_details_class
        if _scale == ScaleSet.CREATE:
            serializer_class = self.serializer_create_class
        elif _scale == ScaleSet.UPDATE:
            serializer_class = self.serializer_update_class
        elif _scale == ScaleSet.DESTROY:
            serializer_class = self.serializer_destroy_class
        return serializer_class

    def get_query_scale(self):
        _scale = None
        if self.action in self.scale_action:
            _scale = self.request.query_params.get("scale")
            if not _scale:
                if self.action == "retrieve":
                    _scale = ScaleSet.DETAIL
                if self.action == "list":
                    _scale = ScaleSet.GENERAL
            if _scale == ScaleSet.MICRO and not self.serializer_micro_class:
                _scale = None
            elif _scale == ScaleSet.DETAIL and not self.serializer_details_class:
                _scale = None

        elif self.action in ("create", "bulk_create") and self.serializer_create_class:
            _scale = ScaleSet.CREATE

        elif self.action in ("update",):
            if self.serializer_update_class:
                _scale = ScaleSet.UPDATE
            elif self.serializer_create_class:
                _scale = ScaleSet.CREATE

        elif self.action in ("destroy", "bulk_destroy") and self.serializer_destroy_class:
            _scale = ScaleSet.DESTROY
        return _scale or ScaleSet.GENERAL

    def get_object(self):
        queryset = self.get_queryset()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        try:
            obj = queryset.get(**filter_kwargs)
        except Exception as e:
            LOG.error(e)
            raise BaseAPIException(code=NOT_FOUND)

        self.check_object_permissions(self.request, obj)
        return obj

    def options(self, request, *args, **kwargs):
        """
        Handler method for HTTP "OPTIONS" request.
        """
        if self.metadata_class is None:
            return self.http_method_not_allowed(request, *args, **kwargs)
        data = self.metadata_class().determine_metadata(request, self)
        return APIResponse(data, status=status.HTTP_200_OK)



def _check_attr_name(func, name):
    assert func.__name__ == name, (
        'Expected function (`{func.__name__}`) to match its attribute name '
        '(`{name}`). If using a decorator, ensure the inner function is '
        'decorated with `functools.wraps`, or that `{func.__name__}.__name__` '
        'is otherwise set to `{name}`.').format(func=func, name=name)
    return func


def _is_extra_action(attr):
    return hasattr(attr, "mapping") and isinstance(attr.mapping, MethodMapper)


class ViewMixin:
    def initialize_request(self, request, *args, **kwargs):
        """
        Set the `.action` attribute on the view, depending on the request method.
        """
        request = super().initialize_request(request, *args, **kwargs)
        method = request.method.lower()
        if method == "options":
            # This is a special case as we always provide handling for the
            # options method in the base `View` class.
            # Unlike the other explicitly defined actions, "metadata" is implicit.
            self.action = "metadata"
        else:
            self.action = self.action_map.get(method, method)
        return request

    def reverse_action(self, url_name, *args, **kwargs):
        """
        Reverse the action for the given `url_name`.
        """
        url_name = "%s-%s" % (self.basename, url_name)
        namespace = None
        if self.request and self.request.resolver_match:
            namespace = self.request.resolver_match.namespace
        if namespace:
            url_name = namespace + ":" + url_name

        kwargs.setdefault("request", self.request)

        return reverse(url_name, *args, **kwargs)

    @classmethod
    def get_extra_actions(cls):
        """
        Get the methods that are marked as an extra ViewSet `@action`.
        """
        return [_check_attr_name(method, name)
                for name, method
                in getmembers(cls, _is_extra_action)]

    @classmethod
    def as_view(cls, **initkwargs):
        if isinstance(getattr(cls, "queryset", None), models.query.QuerySet):
            def force_evaluation():
                raise RuntimeError(
                    "Do not evaluate the `.queryset` attribute directly, "
                    "as the result will be cached and reused between requests. "
                    "Use `.all()` or call `.get_queryset()` instead."
                )

            cls.queryset._fetch_all = force_evaluation

        actions = getattr(cls, "action_map", None)
        if isinstance(actions, dict):
            if "actions" not in initkwargs:
                initkwargs["actions"] = actions.copy()
            else:
                actions.update(initkwargs["actions"])
                initkwargs["actions"] = actions.copy()
        else:
            initkwargs["actions"] = {}
            cls.action_map = {}

        extra_actions = cls.get_extra_actions()
        for action in extra_actions:
            initkwargs["actions"].update(action.mapping)
            cls.action_map.update(action.mapping)

        for method, action in cls.action_map.items():
            handler = getattr(cls, action, None)
            if handler and not hasattr(cls, method):
                setattr(cls, method, handler)

        def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            if hasattr(self, "get") and not hasattr(self, "head"):
                self.head = self.get

            self.setup(self, request, *args, **kwargs)

            # And continue as usual
            return self.dispatch(request, *args, **kwargs)

        view.cls = cls
        view.actions = initkwargs["actions"]
        view.initkwargs = initkwargs

        return csrf_exempt(view)

    def setup(self, request, *args, **kwargs):
        """Initialize attributes shared by all view methods."""
        self.request = request
        self.args = args
        self.kwargs = kwargs


class APIGenericView(ViewMixin, GenericAPIView):
    pass


class GenericViewSet(vs.ViewSetMixin, GenericAPIView):
    pass
