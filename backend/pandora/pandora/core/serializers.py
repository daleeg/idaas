import uuid
import logging
import json
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from django.db.utils import IntegrityError
from django.db.models import F
from rest_framework import serializers
from rest_framework import fields
from pandora.core.exceptions import CreateError, LicenseLimitOut, LicenseExpiring

LOG = logging.getLogger(__name__)


class SlugRelatedField(serializers.RelatedField):
    """
    A read-write field that represents the target of the relationship
    by a unique 'slug' attribute.
    """
    default_error_messages = {
        'does_not_exist': _('{slug_name}={value} 不存在.'),
        'invalid': _('参数无效.'),
        'unknown': _('其他错误, 详情: {e}'),
    }

    def __init__(self, slug_field="uid", serializer=None, insert_field=None, **kwargs):
        assert slug_field is not None, 'The `slug_field` argument is required.'
        self.slug_field = slug_field
        self.serializer = serializer
        self.insert_field = insert_field
        self.implicit = kwargs.pop("implicit", False)
        super(SlugRelatedField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        if not data:
            return None
        if isinstance(data, dict):
            filter_data = data
        else:
            filter_data = {self.slug_field: data}
        if self.insert_field:
            insert_field_data = getattr(self.context.get("view"), self.insert_field, None)
            if insert_field_data:
                filter_data[self.insert_field] = insert_field_data
        try:
            queryset = self.get_queryset().filter(**filter_data)
        except (TypeError, ValueError):
            self.fail('invalid')
        except Exception as e:
            self.fail('unknown', e=e)

        if queryset.exists():
            return queryset[0]
        else:
            if isinstance(data, dict):
                return data
            else:
                self.fail('does_not_exist', slug_name=self.slug_field, value=smart_text(data))

    def to_representation(self, obj):
        if self.serializer:
            serializer = self.serializer(obj)
            return serializer.data
        else:
            return getattr(obj, self.slug_field)


class SmallFloatField(serializers.Field):
    MAX_STRING_LENGTH = 8
    default_error_messages = {
        'invalid': _('需要为有效的浮点字符串格式, 如 1.1'),
        'max_string_length': _('点字符串长度最长为8位, 如 123.4567')
    }

    def __init__(self, **kwargs):
        self.max_value = kwargs.pop('max_value', None)
        self.min_value = kwargs.pop('min_value', None)
        super(SmallFloatField, self).__init__(**kwargs)
        if self.max_value is not None:
            message = fields.lazy(
                self.error_messages['max_value'].format,
                fields.six.text_type)(max_value=self.max_value)
            self.validators.append(
                fields.MaxValueValidator(self.max_value * 100, message=message))
        if self.min_value is not None:
            message = fields.lazy(
                self.error_messages['min_value'].format,
                fields.six.text_type)(min_value=self.min_value)
            self.validators.append(
                fields.MinValueValidator(self.min_value * 100, message=message))

    def validate_empty_values(self, data):
        ret, data = super(SmallFloatField, self).validate_empty_values(data)
        if ret:
            data = 0.0
        return ret, data

    def to_internal_value(self, data):
        if isinstance(data, fields.six.text_type) and len(data) > self.MAX_STRING_LENGTH:
            self.fail('max_string_length')
        try:
            data = float(data)
        except (TypeError, ValueError):
            self.fail('invalid')
        data = str(data).split(".")
        data = int("{}{:0<2}".format(data[0], data[1][:2]))
        return data

    def to_representation(self, value):
        return value / 100


class DictJsonField(serializers.DictField):
    default_error_messages = {
        'invalid': _('Value must be valid Dict.')
    }

    def __init__(self, *args, **kwargs):
        super(DictJsonField, self).__init__(*args, **kwargs)

    def get_value(self, dictionary):
        if self.field_name in dictionary:
            data = dictionary[self.field_name]
            if isinstance(data, serializers.six.text_type):
                try:
                    json.loads(data)
                except (TypeError, ValueError):
                    self.fail('invalid')

                class JSONString(serializers.six.text_type):
                    def __new__(cls, value):
                        ret = serializers.six.text_type.__new__(cls, value)
                        ret.is_json_string = True
                        return ret

                return JSONString(dictionary[self.field_name])
            return dictionary.get(self.field_name, serializers.empty)
        return serializers.empty

    def to_internal_value(self, data):
        try:
            if getattr(data, 'is_json_string', False):
                if isinstance(data, serializers.six.binary_type):
                    data = data.decode('utf-8')
                return data
            else:
                return json.dumps(data)
        except (TypeError, ValueError):
            self.fail('invalid')

    def to_representation(self, value):
        try:
            value = json.loads(value)
        except (TypeError, ValueError):
            pass

        if isinstance(value, serializers.six.text_type):
            value = bytes(value.encode('utf-8'))
        return value


class StringListField(serializers.ListField):
    def to_internal_value(self, data):
        return ",".join(super(StringListField, self).to_internal_value(data))

    def to_representation(self, value):
        try:
            value = value.split(",")
            return super(StringListField, self).to_representation(value)
        except (TypeError, ValueError):
            return None


class TimestampField(serializers.DateTimeField):
    def to_representation(self, value):
        if not value:
            return None
        return value.timestamp()


class RelatedModelSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, data=serializers.empty, split_flag="##", **kwargs):
        if data != serializers.empty:
            many = kwargs.get("many", False)
            if not many:
                self.pre_init_data(data, split_flag)
            else:
                for item in data:
                    self.pre_init_data(item, split_flag)

        super(RelatedModelSerializer, self).__init__(instance=instance, data=data, **kwargs)

    def pre_init_data(self, data, split_flag):
        for field in self._writable_fields:
            primitive_value = field.get_value(data)
            if isinstance(field, serializers.ManyRelatedField) and isinstance(primitive_value, str):
                data[field.field_name] = [i.strip() for i in primitive_value.split(split_flag) if i.strip()]
            if isinstance(field, SlugRelatedField) or isinstance(field, serializers.SlugRelatedField):
                if isinstance(primitive_value, dict):
                    if "uid" in primitive_value and not primitive_value["uid"]:
                        primitive_value.pop("uid")
                elif not primitive_value:
                    data[field.field_name] = {}

    def create(self, validated_data):
        related_data = {}
        try:
            for field in self._writable_fields:
                if field.field_name in validated_data:
                    if isinstance(field, SlugRelatedField):
                        field_data = validated_data.pop(field.field_name, None)
                        if field_data:
                            if not field.implicit:
                                if isinstance(field_data, dict):
                                    validated_data[field.field_name] = field.get_queryset().create(**field_data)
                                else:
                                    validated_data[field.field_name] = field_data
                            else:
                                related_data[field] = field_data
                    if isinstance(field, serializers.ManyRelatedField):
                        field_data = validated_data.pop(field.field_name, None)
                        if field_data:
                            related_data[field] = field_data
            instance = self.Meta.model.objects.create(**validated_data)
            info = serializers.model_meta.get_field_info(instance)
            for field, field_objs in related_data.items():
                related_db = getattr(instance, field.field_name)
                if isinstance(field, serializers.ManyRelatedField):
                    if info.relations[field.field_name].to_many:
                        for field_obj in field_objs:
                            if info.relations[field.field_name].has_through_model:
                                if isinstance(field_obj, dict):
                                    field_obj = related_db.target_field.remote_field.model.objects.create(**field_obj)

                                related_db.through.objects.create(
                                    **{related_db.source_field_name: instance,
                                       related_db.target_field_name: field_obj})
                            else:
                                if isinstance(field_obj, dict):
                                    field_obj = related_db.create(**field_obj)
                                related_db.add(field_obj)
                if isinstance(field, SlugRelatedField):
                    if isinstance(field_objs, dict):
                        related_db.create(**field_objs)
                    related_db.add(field_objs)
        except (IntegrityError, LicenseLimitOut, LicenseExpiring):
            raise
        except Exception as e:
            raise CreateError(e)

        return instance

    def update(self, instance, validated_data):
        serializers.raise_errors_on_nested_writes('update', self, validated_data)
        info = serializers.model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        related_data = {}
        foreign_data = {}
        for field in self._writable_fields:
            if isinstance(field, SlugRelatedField):
                if field.field_name in validated_data:
                    foreign_data[field] = validated_data.pop(field.field_name)
            if isinstance(field, serializers.ManyRelatedField):
                if field.field_name in validated_data:
                    if field.field_name in validated_data:
                        related_data[field.field_name] = validated_data.pop(field.field_name)

        for field, field_obj in foreign_data.items():
            if field_obj:
                if isinstance(field_obj, dict):
                    validated_data[field.field_name] = field.get_queryset().create(**field_obj)
                else:
                    validated_data[field.field_name] = field_obj
            else:
                validated_data[field.field_name] = None

        for field_name, field_objs in related_data.items():
            related_db = getattr(instance, field_name)

            real_field_objs = []
            real_field_ids = []
            for field_obj in field_objs:
                if isinstance(field_obj, dict):
                    if info.relations[field_name].has_through_model:
                        field_obj = related_db.target_field.remote_field.model.objects.create(**field_obj)
                    else:
                        field_obj = related_db.create(**field_obj)
                real_field_objs.append(field_obj)
                real_field_ids.append(field_obj.id)

            if info.relations[field_name].has_through_model:
                objs = related_db.through.objects.filter(**{related_db.source_field_name: instance})
                if objs:
                    for obj in objs:
                        obj.delete()
            else:
                try:
                    related_db.clear()
                except:
                    related_db.exclude(id__in=real_field_ids).delete()

            for field_obj in real_field_objs:
                if info.relations[field_name].has_through_model:
                    if isinstance(field_obj, dict):
                        field_obj = related_db.target_field.remote_field.model.objects.create(**field_obj)

                    related_db.through.objects.create(
                        **{related_db.source_field_name: instance,
                           related_db.target_field_name: field_obj})

                else:
                    if isinstance(field_obj, dict):
                        field_obj = related_db.create(**field_obj)
                    related_db.add(field_obj)

        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)
        instance.save()

        return instance


def auto_serializer(data, template):
    """
    :param data: [ 
        {   
            "name": "name1",
            "section": "867584a6-0f0e-4ada-b054-2b847716c258"
        }
    ]
    :param template: {
        "section": {
            "lookup_field": "uid", # default "uid"
            "model": Class,
            "select_related_fields": ["teacher", "teacher__user"],  # default None
            "fields": {
                "name": "name",
                "teacher__name": "teacher__name",
                "teacher__user": "teacher__user__username"
            }
        },
    }
    :return: 
    """
    template_items = template.items()
    for item in data:
        for key, value in template_items:
            if not item[key]:
                continue
            item[key] = str(item[key])
            value.setdefault("key_list", []).append(str(item[key]))
        for key, value in item.items():
            if isinstance(value, uuid.UUID):
                item[key] = str(value)
    for value in template.values():
        model = value["model"]
        lookup_field = value.get("lookup_field", "uid")
        value["lookup_field"] = lookup_field
        key_list = value.get("key_list", [])
        if not key_list:
            continue
        filter_param = {
            "{}__in".format(lookup_field): key_list
        }
        select_related_fields = value.get("select_related_fields")
        out_fields = value["fields"]
        only_fields = []
        value_fields = []
        value_expressions = {}
        for field, field_source in out_fields.items():
            only_fields.append(field_source)
            if field == field_source:
                value_fields.append(field_source)
            else:
                value_expressions[field] = F(field_source)
        if lookup_field not in only_fields:
            only_fields.append(lookup_field)
            value_fields.append(lookup_field)
        queryset = model.objects.filter(**filter_param)
        if select_related_fields is not None:
            queryset = queryset.select_related(*select_related_fields)
        queryset = queryset.only(*only_fields).values(*value_fields, **value_expressions)
        for item in queryset:
            new_item = {}
            for field, field_value in item.items():
                split_fields = field.split("__")
                container = new_item
                for index, field in enumerate(split_fields):
                    if index < len(split_fields) - 1:
                        if field not in container:
                            container[field] = {}
                        container = container[field]
                    else:
                        container[field] = str(field_value) if isinstance(field_value, uuid.UUID) else field_value
            value.setdefault("data", {})[new_item[lookup_field]] = new_item
    template_items = template.items()
    for item in data:
        for key, value in template_items:
            field_value = item[key]
            if not field_value:
                continue
            data_map = value["data"]
            item[key] = data_map.get(field_value)
    return data
