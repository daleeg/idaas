# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from functools import partial

from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _

from pandora.models import Company
from pandora.business.gen import generate_unique_code
from pandora.core.validator import SupperUniqueValidator

LOG = logging.getLogger(__name__)


class CompanySerializer(serializers.ModelSerializer):
    code = serializers.CharField(default=partial(generate_unique_code, Company))

    class Meta:
        model = Company
        read_only_fields = ["uid", "create_time", "update_time", "extra_info"]
        validators = [
            SupperUniqueValidator(
                queryset=Company.objects.all(),
                fields={"name": "名称"},
                message=_("名称已经存在"),
            ),
            SupperUniqueValidator(
                queryset=Company.objects.all(),
                fields={"code": "标识码"},
                message=_("标识码已经存在"),
            ),
        ]


class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("uid", "name", "code", "description",)