# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db import models
import ast


class ListField(models.TextField):
    __metaclass__ = models.SubfieldBase
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, conn, context):
        if not value:
            value = []
        if isinstance(value, list):
            return value
        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if not value:
            return value
        return str(value)
