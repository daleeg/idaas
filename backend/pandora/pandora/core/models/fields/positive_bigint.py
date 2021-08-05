# -*- coding: utf-8 -*-
from django.core import validators
from django.db import connection
from django.utils.datastructures import DictWrapper
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.db.models import BigIntegerField


class PositiveBigIntegerField(BigIntegerField):
    description = _("Big (8 byte) positive integer")

    def get_internal_type(self):
        return "PositiveBigIntegerField"

    @cached_property
    def validators(self):
        range_validators = []
        if connection.vendor != "sqlite":
            range_validators.append(validators.MinValueValidator(0))
            range_validators.append(validators.MaxValueValidator(18446744073709551615))
        return self.default_validators + range_validators

    def db_type(self, connection):
        data_types = {
            "sqlite": "bigint unsigned",
            "mysql": "bigint UNSIGNED",
            "postgresql": "bigint",
            "oracle": "NUMBER(11)",
        }
        data = DictWrapper(self.__dict__, connection.ops.quote_name, "qn_")
        try:
            return data_types[connection.vendor] % data
        except KeyError:
            return None

    def db_parameters(self, connection):
        data_type_check_constraints = {
            "postgresql": '"%(column)s" >= 0',
            "oracle": "%(qn_column)s >= 0",
        }
        type_string = self.db_type(connection)
        try:
            check_string = data_type_check_constraints[connection.vendor]
        except KeyError:
            check_string = None
        return {
            "type": type_string,
            "check": check_string,
        }

    def formfield(self, **kwargs):
        defaults = {"min_value": 0,
                    "max_value": BigIntegerField.MAX_BIGINT * 2 - 1}
        defaults.update(kwargs)
        return super(PositiveBigIntegerField, self).formfield(**defaults)
