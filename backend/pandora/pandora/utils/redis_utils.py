# -*- coding: utf-8 -*-
from django.core.cache import cache


def cache_hset(school, name, key, value, version=None):
    name = 'PANDORA_TASK_PARAMETER:{}-{}'.format(school, name)
    client = cache.client.get_client(write=True)
    name = cache.client.make_key(name, version=version)
    nvalue = cache.client.encode(value)

    return client.hset(name, key, nvalue)


def cache_hgetall(school, name, version=None):
    name = 'PANDORA_TASK_PARAMETER:{}-{}'.format(school, name)
    client = cache.client.get_client(write=True)
    name = cache.client.make_key(name, version=version)

    values = client.hgetall(name)
    result = {}
    for key, value in values.items():
        result[key.decode()] = cache.client.decode(value)
    return result


def cache_hget(school, name, key, version=None):
    name = 'PANDORA_TASK_PARAMETER:{}-{}'.format(school, name)
    client = cache.client.get_client(write=True)
    name = cache.client.make_key(name, version=version)
    value = client.hget(name, key)
    if value:
        value = cache.client.decode(value)
    return value


def cache_hdel(school, name, key, version=None):
    name = 'PANDORA_TASK_PARAMETER:{}-{}'.format(school, name)
    client = cache.client.get_client(write=True)
    name = cache.client.make_key(name, version=version)
    return client.delete(name, key)
