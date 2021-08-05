# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import serializers
from pandora.utils.cacheutils import get_object_info_cache, set_object_info_cache
import logging

LOG = logging.getLogger(__name__)


def get_object_info(db_model, value, field="uid"):
    name = db_model.__name__
    value = str(value).replace("-", "")
    obj_info = get_object_info_cache(name, value)
    if not obj_info:
        try:
            obj = db_model.objects.get(**{field: value})

            class InnerSerializer(serializers.ModelSerializer):
                class Meta:
                    model = db_model

            serializer = InnerSerializer(instance=obj)
            obj_info = serializer.data
            obj_info["instance"] = obj
            set_object_info_cache(name, value, obj_info)
        except (db_model.DoesNotExist, db_model.MultipleObjectsReturned) as e:
            LOG.error(f"Get {name} {value} Failed, {e}")
        except Exception as e:
            LOG.error(f"Bad {name} {value} Params, {e}")

    return obj_info


def get_override_list(source, dest):
    add = []
    remove = []
    update = []

    for item in source:
        if item in dest:
            update.append(item)
        else:
            remove.append(item)
    for item in dest:
        if item not in source:
            add.append(item)
    return add, update, remove
