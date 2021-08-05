# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.cache import cache
import logging

LOG = logging.getLogger(__name__)


def get_login_count(user):
    key = "IDAAS:LOGIN:{}".format(user)
    value = cache.get(key)
    return 0 if value is None else value


def inc_and_get_login_count(user):
    key = f"IDAAS:LOGIN:{user}"
    value = cache.get(key)
    new_value = 1 if value is None else value + 1
    cache.set(key, new_value, 60)
    return new_value


def clear_login_count(user):
    key = f"IDAAS:LOGIN-{user}"
    if key in cache:
        cache.delete(key)


def get_expire_token(key):
    token_key = f"IDAAS:TOKEN-{key}"
    value = cache.get(token_key)
    return value


def set_expire_token(key, value, timeout=1200):
    token_key = f"IDAAS:TOKEN-{key}"
    cache.set(token_key, value, timeout)


def delete_expire_token(key):
    token_key = f"IDAAS:TOKEN-{key}"
    cache.delete(token_key)


def get_object_info_cache(name, key):
    key = f"IDAAS_OBJ_{name.upper()}:{key}"
    value = cache.get(key)
    return value


def set_object_info_cache(name, key, value, timeout=36000):
    key = f"IDAAS_OBJ_{name.upper()}:{key}"
    cache.set(key, value, timeout)


def delete_object_info_cache(name, key):
    key = f"IDAAS_OBJ_{name.upper()}:{key}"
    cache.delete(key)
    
    
def get_company_info(key):
    company_key = "X-COMPANY:{}".format(key)
    value = cache.get(company_key)
    return value


def set_company_info(key, value, timeout=1200):
    company_key = "X-COMPANY:{}".format(key)
    cache.set(company_key, value, timeout)


def delete_company_info(key):
    company_key = "X-COMPANY:{}".format(key)
    cache.delete(company_key)
