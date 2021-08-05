from django.conf import settings
from drf_yasg import openapi as oi
from rest_framework import serializers as rs
from pandora.core.collection import ScaleSet

__all__ = [
    "default_parameters",
    "DestroySerializer",
    "BulkDestroySerializer",
    "ProcessResponseSerializer",
    "AddResponseSerializer",
    "RemoveResponseSerializer",
    "ModifyResponseSerializer",
    "list_parameters",
    "retrieve_parameters",
    "native_parameters",
    "get_uid_list_body",
    "get_uid_body"
]
company_header = oi.Parameter(settings.COMPANY_HEADER_LOWER, oi.IN_HEADER, description="公司标识",
                             type=oi.TYPE_STRING)

auth_header = oi.Parameter("Authorization", oi.IN_HEADER, description="自定义token认证, Basic 1234 or Token 1234",
                           type=oi.TYPE_STRING)

etag_header = oi.Parameter("If-None-Match", oi.IN_HEADER, description="etag",
                           type=oi.TYPE_STRING)

list_scale = oi.Parameter("scale", oi.IN_QUERY, description="列表等级, {}, 默认值为:{}".format(ScaleSet.query_choices(),
                                                                                       ScaleSet.GENERAL),
                          type=oi.TYPE_STRING)

retrieve_scale = oi.Parameter("scale", oi.IN_QUERY, description="详情等级, {}, 默认值为:{}".format(ScaleSet.query_choices(),
                                                                                           ScaleSet.DETAIL),
                              type=oi.TYPE_STRING)

default_parameters = [company_header, auth_header, etag_header]
retrieve_parameters = [company_header, auth_header, etag_header, retrieve_scale]
list_parameters = [company_header, auth_header, etag_header, list_scale]
native_parameters = [auth_header, etag_header]


def get_uid_list_body(description):
    return oi.Schema(type=oi.TYPE_ARRAY, items=oi.Schema(type=oi.TYPE_STRING), description=description)


def get_uid_body(description):
    return oi.Schema(items=oi.Schema(type=oi.TYPE_STRING), description=description)


class DestroySerializer(rs.Serializer):
    soft = rs.BooleanField(default=True, help_text="是否软删")
    force = rs.BooleanField(default=False, help_text="是否强制删除")


class BulkDestroySerializer(DestroySerializer):
    ids = rs.ListSerializer(help_text="uid列表", child=rs.CharField(max_length=32))


class ProcessResponseSerializer(rs.Serializer):
    add = rs.IntegerField(default=0, help_text="添加条数")
    modify = rs.IntegerField(default=0, help_text="修改条数")
    remove = rs.IntegerField(default=0, help_text="删除条数")


class AddResponseSerializer(rs.Serializer):
    add = rs.IntegerField(default=0, help_text="添加条数")


class ModifyResponseSerializer(rs.Serializer):
    modify = rs.IntegerField(default=0, help_text="修改条数")


class RemoveResponseSerializer(rs.Serializer):
    remove = rs.IntegerField(default=0, help_text="删除条数")
