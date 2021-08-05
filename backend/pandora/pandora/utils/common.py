# -*- coding: utf-8 -*-

from collections import OrderedDict


def tohex(num):
    return hex(num)[2:]


def get_bool_from_query(query_params, key, default="true"):
    value = query_params.get(key, default)
    return value.lower() in ("on", "true", "y", "yes", 1)


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


def is_child(obj, cls):
    # if not obj or not cls:
    #     return False
    # return _is_child(obj, cls)
    return issubclass(obj, cls)


def _is_child(obj, cls):
    try:
        for i in obj.__bases__:
            if i is cls or isinstance(i, cls):
                return True
        for i in obj.__bases__:
            if is_child(i, cls):
                return True
    except AttributeError:
        return is_child(obj.__class__, cls)
    return False

