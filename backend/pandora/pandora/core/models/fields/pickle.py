# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from picklefield.fields import PickledObjectField


class UnicodePickledObjectField(PickledObjectField):

    def get_db_prep_value(self, value, connection=None, prepared=False):
        return super(UnicodePickledObjectField, self).get_db_prep_value(value, connection, prepared)
