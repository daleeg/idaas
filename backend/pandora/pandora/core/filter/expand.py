# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import django_filters
from django.http import QueryDict

from pandora.models.collection import ExpandFieldCategory

__all__ = [
    "BaseExpandFilter",
]


class BaseExpandFilter(django_filters.FilterSet):
    system_key = ["search", "page", "page_size", "scale"]

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.filter(**self.expand_data)

    def extract_expand_data(self, data):
        model_str_list, expand_data = [], {}
        current_model = self._meta.model
        clare_fields = self._meta.fields
        keys = list(data.keys())
        for key in keys:
            if not hasattr(current_model, key) and key not in self.system_key and key not in clare_fields:
                expand_key = "expand__{}".format(key)
                expand_data[expand_key] = data.get(key)
            else:
                query_str = "{}={}".format(key, data.get(key))
                model_str_list.append(query_str)
        model_str = "&".join(model_str_list)
        model_data = QueryDict(model_str)
        setattr(self, "expand_data", expand_data)
        return model_data

    def __init__(self, *args, **kwargs):
        model_data = self.extract_expand_data(kwargs["data"])
        kwargs["data"] = model_data
        super(BaseExpandFilter, self).__init__(*args, **kwargs)
