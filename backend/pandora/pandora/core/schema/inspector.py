# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import coreschema
from collections import OrderedDict
from pandora.core.pagination import APIPagination, APIPageNumberPagination
from drf_yasg import openapi
from drf_yasg.inspectors.base import FilterInspector, PaginatorInspector
from drf_yasg.utils import force_real_str

__all__ = ["OpenAPIFilterInspector", "APIRestResponsePagination"]


class BaseInspector(object):
    def openapi_field_to_parameter(self, field):
        in_ = field.pop("in")
        schema = field.pop("schema")
        return openapi.Parameter(in_=in_, type=schema["type"], **field)


    def coreapi_field_to_parameter(self, field):
        """Convert an instance of `coreapi.Field` to a swagger :class:`.Parameter` object.

        :param coreapi.Field field:
        :rtype: openapi.Parameter
        """
        location_to_in = {
            "query": openapi.IN_QUERY,
            "path": openapi.IN_PATH,
            "form": openapi.IN_FORM,
            "body": openapi.IN_FORM,
        }
        coreapi_types = {
            coreschema.Integer: openapi.TYPE_INTEGER,
            coreschema.Number: openapi.TYPE_NUMBER,
            coreschema.String: openapi.TYPE_STRING,
            coreschema.Boolean: openapi.TYPE_BOOLEAN,
        }

        coreschema_attrs = ["format", "pattern", "enum", "min_length", "max_length"]
        schema = field.schema
        return openapi.Parameter(
            name=field.name,
            in_=location_to_in[field.location],
            required=field.required,
            description=force_real_str(schema.description) if schema else None,
            type=coreapi_types.get(type(schema), openapi.TYPE_STRING),
            **OrderedDict((attr, getattr(schema, attr, None)) for attr in coreschema_attrs)
        )


class OpenAPIFilterInspector(BaseInspector, FilterInspector):
    """Converts ``coreapi.Field``\\ s to :class:`.openapi.Parameter`\\ s for filters and paginators that implement a
    ``get_schema_fields`` method.
    """

    def get_filter_parameters(self, filter_backend):
        parameters = []
        if hasattr(filter_backend, "get_schema_operation_parameters"):
            fields = filter_backend.get_schema_operation_parameters(self.view)
            parameters += [self.openapi_field_to_parameter(field) for field in fields]
        elif hasattr(filter_backend, "get_schema_fields"):
            fields = filter_backend.get_schema_fields(self.view)
            parameters += [self.coreapi_field_to_parameter(field) for field in fields]
        return parameters


class APIRestResponsePagination(BaseInspector, PaginatorInspector):
    """Provides response schema pagination warpping for django-rest-framework"s LimitOffsetPagination,
    PageNumberPagination and CursorPagination
    """

    def get_paginator_parameters(self, paginator):
        parameters = []
        if hasattr(paginator, "get_schema_operation_parameters"):
            fields = paginator.get_schema_operation_parameters(self.view)
            parameters += [self.openapi_field_to_parameter(field) for field in fields]
        elif hasattr(paginator, "get_schema_fields"):
            fields = paginator.get_schema_fields(self.view)
            parameters += [self.coreapi_field_to_parameter(field) for field in fields]
        return parameters

    def get_paginated_response(self, paginator, response_schema):
        assert response_schema.type == openapi.TYPE_ARRAY, "array return expected for paged response"
        paged_schema = None
        if isinstance(paginator, APIPagination):
            links_schema = openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=OrderedDict((
                    ("next", openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, x_nullable=True)),
                    ("previous", openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, x_nullable=True))
                )),

            )
            paged_schema = openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=OrderedDict((
                    ("count", openapi.Schema(type=openapi.TYPE_INTEGER)),
                    ("links", links_schema),
                    ("results", response_schema),

                )),
                required=["count", "results"]
            )
        elif isinstance(paginator, APIPageNumberPagination):
            pages_schema = openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=OrderedDict((
                    ("page", openapi.Schema(type=openapi.TYPE_INTEGER)),
                    ("page_size", openapi.Schema(type=openapi.TYPE_INTEGER))
                )),
            )
            paged_schema = openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=OrderedDict((
                    ("count", openapi.Schema(type=openapi.TYPE_INTEGER)),
                    ("total", openapi.Schema(type=openapi.TYPE_INTEGER)),
                    ("pages", pages_schema),
                    ("results", response_schema),

                )),
                required=["count", "results"]
            )

        return paged_schema
