#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import json
import os
import binascii
from django.db import models
from django.contrib.auth.models import (AbstractUser, BaseUserManager)
from django.utils.translation import ugettext_lazy as _
from pandora.core.models import BaseQuerySet
from pandora.models import ExtraBaseModel

__all__ = [
    'User',
]


class UserManager(BaseUserManager):
    use_in_migrations = True
    _queryset_class = BaseQuerySet

    def _create_user(self, username, password, direct, **extra_fields):
        """
        Creates and saves a User with the given username, password.
        """
        if not username:
            raise ValueError('The given username must be set')
        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        if not direct:
            user.set_password(password)
        else:
            user.password = password
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, direct=False, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, direct=direct, **extra_fields)

    def create_staffuser(self, username, password=None, direct=False, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, direct=direct, **extra_fields)

    def create_superuser(self, username, password, direct=False, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, direct=direct, **extra_fields)

    def get_queryset(self):
        """
        在这里处理一下QuerySet, 然后返回没被标记位is_deleted的QuerySet
        """
        kwargs = {'model': self.model, 'using': self._db}
        if hasattr(self, '_hints'):
            kwargs['hints'] = self._hints
        return self._queryset_class(**kwargs).filter(is_deleted=False)


class User(AbstractUser, ExtraBaseModel):
    specific = models.CharField(help_text=_('个性化信息, str(2048)'), max_length=2048, blank=True, null=True)
    avatar = models.CharField(help_text=_("图片访问URL, str(256)"), max_length=256, blank=True, null=True)
    extra_info = models.TextField(help_text=_('额外信息'), blank=True, null=True)

    objects = UserManager()
    REQUIRED_FIELDS = []

    @classmethod
    def generate_username(cls, prefix):
        # count = cls.objects.filter(username__startswith=prefix).count()
        # if count:
        #     prefix = "{}_{:02}".format(prefix, count)
        for _ in range(10):
            name = "{}_{}".format(prefix, binascii.hexlify(os.urandom(2)).decode())
            try:
                cls.objects.get(username=name)
            except cls.DoesNotExist:
                return name
        return name

    def get_extra_info(self, key):
        try:
            extra_info = json.loads(self.extra_info)
            value = extra_info.get(key)
        except (Exception,):
            value = None
        return value

