# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from collections import OrderedDict
from django.apps import AppConfig
from functools import lru_cache

__all__ = ["PandoraConfig"]


class PandoraConfig(AppConfig):
    name = "pandora"
    verbose_name = "pandora"

    def ready(self):
        import pandora.utils.parallel
        import pandora.signal
        from django.db.models import BigIntegerField as dj_BigIntegerField
        from rest_framework import fields
        from rest_framework import serializers

        from rest_framework.utils import model_meta

        from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList
        from rest_framework.exceptions import ErrorDetail
        from rest_framework.settings import api_settings
        from django.urls.converters import UUIDConverter
        UUIDConverter.regex = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|[0-9a-f]{32}"

        def _get_fields(opts):
            fields = OrderedDict()
            for field in [field for field in opts.fields if field.serialize and not field.remote_field]:
                if field.name == "is_deleted":
                    continue
                fields[field.name] = field
            return fields

        # def errors(this):
        #     if not hasattr(this, "_errors"):
        #         msg = "You must call `.is_valid()` before accessing `.errors`."
        #         raise AssertionError(msg)
        #     ret = this._errors
        #     if isinstance(ret, list) and len(ret) == 1 and getattr(ret[0], "code", None) == "null":
        #         # Edge case. Provide a more descriptive error than
        #         # "this field may not be null", when no data is passed.
        #         detail = ErrorDetail("No data provided", code="null")
        #         ret = {api_settings.NON_FIELD_ERRORS_KEY: [detail]}
        #     if isinstance(ret, dict):
        #         return ReturnDict(ret, serializer=this)
        #     return ReturnList(ret, serializer=this)

        class ModelSerializerMetaclass(serializers.SerializerMetaclass):
            def __new__(cls, name, bases, attrs):
                new_class = super().__new__(cls, name, bases, attrs)
                meta = getattr(new_class, "Meta", None)
                if meta:
                    fields = getattr(meta, "fields", None)
                    exclude = getattr(meta, "exclude", None)
                    if not fields and not exclude:
                        meta.fields = serializers.ALL_FIELDS
                    model = getattr(meta, "model")
                    info = model_meta.get_field_info(model)
                    field_map = {}
                    for field in info.forward_relations:
                        model_field = info.forward_relations[field]
                        if not model_field.to_many:
                            field_id = "{}_id".format(field)
                            field_map[field] = field_id
                            field_map[field_id] = field
                    setattr(meta, "field_map", field_map)
                return new_class

        class ModelSerializer(serializers.ModelSerializer, metaclass=ModelSerializerMetaclass):
            def get_default_field_names(self, declared_fields, model_info):
                """
                Return the default list of field names that will be used if the
                `Meta.fields` option is not specified.
                """
                default_fields = super(ModelSerializer, self).get_default_field_names(declared_fields, model_info)
                for index, field in enumerate(default_fields):
                    if field in self.Meta.field_map and field not in declared_fields:
                        default_fields[index] = self.Meta.field_map[field]
                return list(set(default_fields))

            def build_field(self, field_name, info, model_class, nested_depth):
                model_field_name = field_name.rstrip("_id")
                if model_field_name in info.forward_relations:
                    model_field = info.forward_relations[model_field_name]
                    if not model_field.to_many:
                        new_field = dj_BigIntegerField(help_text="{},{}".format(model_field.model_field.help_text,
                                                                                model_field.to_field),
                                                       blank=model_field.model_field.blank,
                                                       null=model_field.model_field.null, )
                        return self.build_standard_field(field_name, new_field)

                return super(ModelSerializer, self).build_field(field_name, info,
                                                                model_class, nested_depth)

        model_meta._get_fields = _get_fields
        model_meta.get_field_info = lru_cache(None)(model_meta.get_field_info)
        serializers.ModelSerializer = ModelSerializer
        from django_mysql.models import JSONField, ListTextField
        # serializers.ModelSerializer.serializer_field_mapping[JSONField] = serializers.JSONField
        # serializers.ModelSerializer.serializer_field_mapping[ListTextField] = serializers.JSONField
        # serializers.Serializer.errors = property(errors)
