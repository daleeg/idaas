# -*- coding: utf-8 -*-

import uuid
from collections import OrderedDict


def check_uuid(v):
    try:
        uuid.UUID(v)
        return v
    except:
        return False


def get_uuid_list_from_list(v):
    return list(filter(lambda x: check_uuid(x), v))


def get_uuid_list_from_string(v, schema=","):
    return list(filter(lambda x: check_uuid(x), v.strip().split(schema)))


def get_uuid_list(v):
    if isinstance(v, list):
        return get_uuid_list_from_list(v)
    elif isinstance(v, str):
        return get_uuid_list_from_string(v)
    raise Exception("bad type {}".format(type(v)))


def get_bool_from_query(query_params, key, default="true"):
    value = query_params.get(key, default)
    return value.lower() in ('on', 'true', 'y', 'yes', 1)


def type_2_str(item):
    if isinstance(item, dict):
        result = "{"
        for key, value in sorted(item.items()):
            result += "{}:{},".format(type_2_str(key), type_2_str(value))
        result += "}"
        return result
    if isinstance(item, OrderedDict):
        result = "{"
        for key, value in item.items():
            result += "{}:{},".format(type_2_str(key), type_2_str(value))
        result += "}"
        return result
    if isinstance(item, list):
        result = "["
        for value in item:
            result += "{},".format(type_2_str(value))
        result += "]"
        return result
    if isinstance(item, tuple):
        result = "("
        for value in item:
            result += "{},".format(type_2_str(value))
        result += ")"
        return result

    return "{}".format(item)
