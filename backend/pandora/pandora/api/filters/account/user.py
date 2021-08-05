# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import django_filters
from pandora.core.filter import BaseExpandFilter
from pandora import models

__all__ = [
    'UserFilter'
]


class UserFilter(BaseExpandFilter):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = models.User
        fields = ['name']
