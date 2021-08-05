# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework.filterset import FilterSet
from rest_framework.filters import SearchFilter
from django_filters.constants import ALL_FIELDS


def filter_pass(queryset, name, value):
    return queryset


class APIFilterSet(FilterSet):
    pass


class APIDjangoFilterBackend(DjangoFilterBackend):
    default_filter_set = APIFilterSet


class APISearchFilter(SearchFilter):
    pass


def filterset_factory(model, fields=ALL_FIELDS):
    meta = type(str("Meta"), (object,), {"model": model, "fields": fields})
    filterset = type(str("%sFilterSet" % model._meta.object_name),
                     (APIFilterSet,), {"Meta": meta})
    return filterset
