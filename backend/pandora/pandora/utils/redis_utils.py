# -*- coding: utf-8 -*-
from django.core.cache import cache


def cache_hset(name, key, value, version=None):
    name = f"IDAAS-HSET:{name}"
    client = cache.client.get_client(write=True)
    name = cache.client.make_key(name, version=version)
    nvalue = cache.client.encode(value)

    return client.hset(name, key, nvalue)


def cache_hgetall(name, version=None):
    name = f"IDAAS-HSET:{name}"
    client = cache.client.get_client(write=True)
    name = cache.client.make_key(name, version=version)

    values = client.hgetall(name)
    result = {}
    for key, value in values.items():
        result[key.decode()] = cache.client.decode(value)
    return result


def cache_hget(name, key, version=None):
    name = f"IDAAS-HSET:{name}"
    client = cache.client.get_client(write=True)
    name = cache.client.make_key(name, version=version)
    value = client.hget(name, key)
    if value:
        value = cache.client.decode(value)
    return value


def cache_hdel(name, key, version=None):
    name = f"IDAAS-HSET:{name}"
    client = cache.client.get_client(write=True)
    name = cache.client.make_key(name, version=version)
    return client.delete(name, key)
