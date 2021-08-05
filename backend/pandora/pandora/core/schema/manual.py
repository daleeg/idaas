# from rest_framework.schemas.coreapi import AutoSchema
import logging
import coreapi
import uritemplate
from collections import OrderedDict, defaultdict
from django.utils.encoding import smart_str
from rest_framework.utils import formatting
from rest_framework.schemas import AutoSchema
from rest_framework.schemas.generators import endpoint_ordering
from django.urls import URLPattern, URLResolver
from rest_framework.compat import coreschema
from drf_yasg import openapi
from drf_yasg.inspectors.base import call_view_method
from drf_yasg.utils import guess_response_status, no_body, force_serializer_instance
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.generators import EndpointEnumerator as _EndpointEnumerator
from drf_yasg.generators import OpenAPISchemaGenerator as _OpenAPISchemaGenerator
from drf_yasg.errors import SwaggerGenerationError

LOG = logging.getLogger(__name__)

STRING = coreschema.String
NUMBER = coreschema.Number
BOOL = coreschema.Boolean
ANY = coreschema.Anything
ARRAY = coreschema.Array
ENUM = coreschema.Enum
INTEGER = coreschema.Integer
UNION = coreschema.Union
OBJECT = coreschema.Object
QUERY = "query"
FORM = "form"
BODY = "body"
PATH = "path"
HEADER = "header"
ManualField = coreapi.Field


class ManualField(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class ManualViewSchema(AutoSchema):
    def __init__(self, **kwargs):
        """
        Parameters:

        * `manual_fields`: list of `coreapi.Field` instances that
            will be added to auto-generated fields, overwriting on `Field.name`
        """
        self._manual_kwargs = kwargs
        super(ManualViewSchema, self).__init__()

    def get_manual_fields(self, path, method):
        action = getattr(self.view, "action", None)
        extra = getattr(self.view, "extra_manual_schema", {})

        manual_fields = self._manual_kwargs.get(method.lower(), []) + extra.get(method.lower(), [])
        if action:
            manual_fields += self._manual_kwargs.get(action, [])

        manual_fields += self._manual_kwargs.get("all", [])

        manual_fields = {field.name: field for field in manual_fields if hasattr(field, "name")}.values()

        return [
            coreapi.Field(
                name=field.name,
                required=field.__dict__.get("required", False),
                location=field.__dict__.get("location", QUERY if method.lower() in ["get", ] else FORM),
                schema=field.__dict__.get("schema", STRING()),
                description=field.__dict__.get("description", None),
                example=field.__dict__.get("example", None)
            ) for field in manual_fields if hasattr(field, "name")
        ]

    def _allows_filters(self, path, method):
        if getattr(self.view, "filter_backends", None) is None:
            return False

        if hasattr(self.view, "action"):
            return self.view.action in ["list", "bulk_destroy", ]

        return method.lower() in ["get", "delete"]

    @staticmethod
    def update_fields(fields, update_with):
        """
        Update list of coreapi.Field instances, overwriting on `Field.name`.

        Utility function to handle replacing coreapi.Field fields
        from a list by name. Used to handle `manual_fields`.

        Parameters:

        * `fields`: list of `coreapi.Field` instances to update
        * `update_with: list of `coreapi.Field` instances to add or replace.
        """
        if not update_with:
            return fields

        by_name = OrderedDict(((f.name, f.location), f) for f in fields)
        for f in update_with:
            by_name[(f.name, f.location)] = f
        fields = list(by_name.values())
        return fields

    def get_description(self, path, method):
        view = self.view

        method_name = getattr(view, "action", method.lower())
        method_docstring = getattr(view, method_name, None).__doc__ or getattr(view, method.lower(), None).__doc__
        if method_docstring:
            # An explicit docstring on the method or action.
            return self._get_description_section(view, method.lower(), formatting.dedent(smart_str(method_docstring)))
        else:
            return self._get_description_section(view, getattr(view, "action", method.lower()),
                                                 view.get_view_description())


class EndpointEnumerator(_EndpointEnumerator):
    def get_api_endpoints(self, patterns=None, prefix="", app_name=None, namespace=None, ignored_endpoints=None):
        """
        Return a list of all available API endpoints by inspecting the URL conf.

        Copied entirely from super.
        """
        if patterns is None:
            patterns = self.patterns

        api_endpoints = []
        if ignored_endpoints is None:
            ignored_endpoints = set()

        for pattern in patterns:
            path_regex = prefix + str(pattern.pattern)
            if isinstance(pattern, URLPattern):
                try:
                    path = self.get_path_from_regex(path_regex)
                    callback = pattern.callback
                    from pandora.core.endpoints.viewjoin import ViewJoin
                    url_name = pattern.name
                    if isinstance(callback, ViewJoin):
                        for method in callback.actions:
                            handler_callback = callback.handler_view(method)
                            if self.should_include_endpoint(path, handler_callback, app_name or "", namespace or "",
                                                            url_name):
                                path = self.replace_version(path, handler_callback)
                                for method in self.get_allowed_methods(handler_callback):
                                    endpoint = (path, method, handler_callback)
                                    if endpoint in ignored_endpoints:
                                        continue
                                    ignored_endpoints.add(endpoint)
                                    api_endpoints.append(endpoint)

                    else:
                        if self.should_include_endpoint(path, callback, app_name or "", namespace or "", url_name):
                            path = self.replace_version(path, callback)

                            for method in self.get_allowed_methods(callback):
                                endpoint = (path, method, callback)
                                if endpoint in ignored_endpoints:
                                    continue
                                ignored_endpoints.add(endpoint)
                                api_endpoints.append(endpoint)
                except Exception:  # pragma: no cover
                    LOG.warning("failed to enumerate view", exc_info=True)

            elif isinstance(pattern, URLResolver):
                nested_endpoints = self.get_api_endpoints(
                    patterns=pattern.url_patterns,
                    prefix=path_regex,
                    app_name="%s:%s" % (app_name, pattern.app_name) if app_name else pattern.app_name,
                    namespace="%s:%s" % (namespace, pattern.namespace) if namespace else pattern.namespace,
                    ignored_endpoints=ignored_endpoints
                )
                api_endpoints.extend(nested_endpoints)
            else:
                LOG.warning("unknown pattern type {}".format(type(pattern)))

        api_endpoints = sorted(api_endpoints, key=endpoint_ordering)
        return api_endpoints


class OpenAPISchemaGenerator(_OpenAPISchemaGenerator):
    """
    This class iterates over all registered API endpoints and returns an appropriate OpenAPI 2.0 compliant schema.
    Method implementations shamelessly stolen and adapted from rest-framework ``SchemaGenerator``.
    """
    endpoint_enumerator_class = EndpointEnumerator

    def get_endpoints(self, request):
        enumerator = self.endpoint_enumerator_class(self._gen.patterns, self._gen.urlconf, request=request)
        endpoints = enumerator.get_api_endpoints()
        print("endpoints: {}".format(len(endpoints)))
        view_paths = defaultdict(list)
        view_cls = {}
        for path, method, callback in endpoints:
            view = self.create_view(callback, method, request)
            path = self.coerce_path(path, view)
            view_paths[path].append((method, view))
            view_cls[path] = callback.cls
        return {path: (view_cls[path], methods) for path, methods in view_paths.items()}


class ManualSwaggerAutoSchema(SwaggerAutoSchema):
    implicit_list_response_methods = ("GET", "POST", "DELETE")

    def get_tags(self, operation_keys=None):
        operation_keys = operation_keys or self.operation_keys
        tags = self.overrides.get("tags")
        if not tags:
            len_operation_keys = len(operation_keys)
            if len_operation_keys > 1:
                tag_keys = operation_keys[:-1]
            else:
                tag_keys = operation_keys[::]

            tags = ["/".join(tag_keys)]
        return tags

    def __init__(self, view, path, method, components, request, overrides, operation_keys=None):
        super(SwaggerAutoSchema, self).__init__(view, path, method, components, request, overrides)
        self._sch = ManualViewSchema()
        self._sch.view = view
        self.operation_keys = operation_keys

    def get_request_body_schema(self, serializer):
        """Return the :class:`.Schema` for a given request's body data. Only applies to PUT, PATCH and POST requests.

        :param serializer: the view's request serializer as returned by :meth:`.get_request_serializer`
        :rtype: openapi.Schema
        """
        schema = super(ManualSwaggerAutoSchema, self).get_request_body_schema(serializer)
        if self.has_list_request_body():
            schema = openapi.Schema(type=openapi.TYPE_ARRAY, items=schema)
        return schema

    def has_list_request_body(self):
        view = self.view
        action = getattr(view, "action", "")
        method = getattr(view, action, None) or self.method
        if action in ("bulk_create",):
            return True
        many = getattr(method, "many", False)
        return many

    def get_default_responses(self):
        method = self.method.lower()

        default_status = guess_response_status(method)
        default_schema = ""
        if method in ("get", "post", "put", "patch"):
            default_schema = self.get_default_response_serializer()

        default_schema = default_schema or ""
        if default_schema and not isinstance(default_schema, openapi.Schema):
            default_schema = self.serializer_to_schema(default_schema) or ""
        if default_schema:
            if self.has_list_response():
                default_schema = openapi.Schema(type=openapi.TYPE_ARRAY, items=default_schema)
            if self.should_page():
                default_schema = self.get_paginated_response(default_schema) or default_schema
        default_schema = default_schema or openapi.Schema(type=openapi.TYPE_OBJECT)

        if not self.view.native_response:
            default_schema = openapi.Schema(type=openapi.TYPE_OBJECT, properties=OrderedDict(
                code=openapi.Schema(type=openapi.TYPE_NUMBER),
                message=openapi.Schema(type=openapi.TYPE_STRING),
                data=default_schema
            ))

        return OrderedDict({str(default_status): default_schema})

    def is_list_view(self):
        path, method, view = self.path, self.method, self.view
        action = getattr(view, "action", "")
        method = getattr(view, action, None) or method
        detail = getattr(method, "detail", None)
        suffix = getattr(view, "suffix", None)

        if action in ("bulk_create", "bulk_destroy",):
            return True

        if action in ("list",) and suffix != "Instance":
            return True

        if detail is False and suffix == "List":
            # a detail action is surely not a list route
            return True

        # otherwise assume it"s a list view
        return False

    def get_default_response_serializer(self):
        """Return the default response serializer for this endpoint. This is derived from either the ``request_body``
        override or the request serializer (:meth:`.get_view_serializer`).

        :return: response serializer, :class:`.Schema`, :class:`.SchemaRef`, ``None``
        """
        body_override = self._get_response_body_override()
        if body_override and body_override is not no_body:
            return body_override
        return call_view_method(self.view, "get_response_serializer")

    def _get_response_body_override(self):
        body_override = self.overrides.get("response_body", None)

        if body_override is not None:
            if body_override is no_body:
                return no_body
            if self.method not in self.body_methods:
                raise SwaggerGenerationError("request_body can only be applied to (" + ",".join(self.body_methods) +
                                             "); are you looking for query_serializer or manual_parameters?")
            if isinstance(body_override, openapi.Schema.OR_REF):
                return body_override
            return force_serializer_instance(body_override)

        return body_override

    def get_filter_parameters(self):
        if not self.should_filter():
            return []
        fields = []
        # for filter_backend in getattr(self.view, "filter_backends"):
        #     fields += self.probe_inspectors(self.filter_inspectors, "get_filter_parameters", filter_backend()) or []
        filter_backends = getattr(self.view, "filter_backends")

        for filter_backend in filter_backends:
            fields += self.probe_inspectors(self.filter_inspectors, "get_filter_parameters", filter_backend()) or []

        return self.filter_path_parameters(fields)

    def filter_path_parameters(self, fields):
        path_fields = [variable for variable in sorted(uritemplate.variables(self.path))]
        fields = [field for field in fields if field.name not in path_fields]
        return fields

    def split_summary_from_description(self, description):
        summary_max_len = 120
        sections = description.split("\n\n", 1)
        summary = sections[0].strip()[:summary_max_len]
        if len(sections) == 2:
            description = sections[1].strip()
        else:
            description = sections[0].strip()
        return summary, description
