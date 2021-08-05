# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.cache import caches
from django.utils import timezone
from .dependents import LEVEL_COMPANY, LEVEL_ALL, REFRESH_EVERY_GET_ITEMS
from django.conf import settings
import random

import logging

LOG = logging.getLogger(__name__)
cache = caches[settings.API_CACHE_REDIS]


def gen_seed_value():
    return int(timezone.now().timestamp())


def gen_day_seed_value():
    return int(timezone.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp())


def set_table_last_modify(key, value, timeout=None):
    cache.set(key, value, timeout)
    return value


def refresh_table(table, code, level=LEVEL_COMPANY):
    key = "{}_{}_{}".format(table.upper(), level, code)
    value = gen_seed_value()
    return set_table_last_modify(key, value)


def refresh_tables(tables):
    keys = ["{}_{}_{}".format(table[0].upper(), table[1], table[2]) for table in tables]
    value = gen_seed_value()
    returns = []
    for key in keys:
        returns.append(set_table_last_modify(key, value))
    return returns


def get_instant_table_data(tables):
    data = {}
    day_value = gen_day_seed_value()
    for table, level, code in tables:
        if table.upper() in REFRESH_EVERY_GET_ITEMS:
            key = "{}_{}_{}".format(table.upper(), level, code)
            data[key] = day_value
    return data


def get_tables_last_modify(tables):
    keys = ["{}_{}_{}".format(table[0].upper(), table[1], table[2]) for table in tables]
    instant_table_data = get_instant_table_data(tables)
    data = cache.get_many(keys)
    LOG.debug(keys)
    result = []
    for key in keys:
        value = gen_seed_value()
        if key in instant_table_data:
            result.append(str(instant_table_data[key]))
            continue
        if key not in data:
            item = cache.get(key)
            if not item:
                set_table_last_modify(key, value)
                result.append(str(value))
            else:
                result.append(str(item))
                data[key] = item
        else:
            result.append(str(data[key]))

    LOG.debug(result)
    return result


def _cache_set(key, data, ticket, timeout=3600 * 4):
    value = {
        "data": data,
        "ticket": ticket
    }
    if isinstance(timeout, int):
        timeout = random.randint(timeout, timeout << 1)
    cache.set(key, value, timeout)
    return value


def set_api_data(key, data, ticket, timeout=3600 * 4):
    key = "API:{}".format(key)
    return _cache_set(key, data, ticket, timeout)


def get_api_data(key):
    key = "API:{}".format(key)
    return cache.get(key)


def set_cache_data(key, data, ticket, timeout=3600 * 4):
    return _cache_set(key, data, ticket, timeout)


def get_cache_data(key):
    return cache.get(key)
