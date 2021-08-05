# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import functools
from importlib import import_module
from django.conf import settings
from .cache import get_api_data, get_tables_last_modify, set_api_data, refresh_table
from .cache import set_cache_data, get_cache_data
from .ticket import gen_key, check_ticket, gen_ticket, make_params_key
from .dependents import LEVEL_COMPANY, LEVEL_ALL
from .dependents import LEVEL_SET
from .dependents import CATEGORY_INNER
from pandora.core.response import APIResponse
from pandora.models import Company

dependency = import_module(settings.CACHE_DEPENDENCY_MAPPING)
mapping = dependency.mapping

import logging

LOG = logging.getLogger(__name__)

METHOD_ACTIONS = ["GET", ]


def refresh_all_cache_tables(tables):
    result = dict.fromkeys(LEVEL_SET, 0)
    for level, tables in tables.items():
        if level == LEVEL_COMPANY:
            companys = Company.objects.all()
            for table in tables:
                for company in companys:
                    refresh_table(table, company.uid, level)
                    result[level] += 1

        elif level == LEVEL_ALL:
            for table in tables:
                refresh_table(table, "", level)
                result[level] += 1

    return result


def refresh_table_dependency(table, instance):
    levels = mapping.get_table_levels(table)
    for level in levels:
        if level == LEVEL_COMPANY:
            refresh_company_instance_cache_table(table, instance)
        elif level == LEVEL_ALL:
            refresh_table(table, "", level)


def refresh_company_cache_table(table, company_id):
    if table not in mapping.DEPENDENTS_LEVEL_ITEM_MAP[LEVEL_COMPANY]:
        LOG.debug("Table {}-{}".format(table, company_id))
    else:
        LOG.debug("Cache Table {}-{}".format(table, company_id))
        refresh_table(table, company_id)


def refresh_all_cache_table(table):
    if table not in mapping.DEPENDENTS_LEVEL_ITEM_MAP[LEVEL_ALL]:
        LOG.debug("All Table {}".format(table))
    else:
        LOG.debug("Cache ALL Table {}".format(table))
        refresh_table(table, code="", level=LEVEL_ALL)


def refresh_company_instance_cache_table(table, instance):
    if table in ["Company"]:
        company_id = instance.uid
    else:
        company_id = instance.company_id
    LOG.debug("Cache Company Table {}-{}".format(table, company_id))
    if company_id:
        refresh_table(table, code=company_id, level=LEVEL_COMPANY)


def get_api_cache_data(company, path, ticket):
    key = "API:{}".format(gen_key([path, company]))
    LOG.debug("key: {}".format(key))
    LOG.debug("company: {}".format(company))
    data = get_api_data(key)
    if not data:
        return False, None

    old_ticket = data.get("ticket", None)
    result = data.get("data", None)
    LOG.debug("ticket get: {}".format(old_ticket))
    if ticket != old_ticket:
        return False, None
    response = APIResponse(data=result.get("result"), headers=result.get("headers"))
    return True, response.json_render()


def can_cache(company, user, path, method):
    if method.upper() not in METHOD_ACTIONS:
        return False
    # if not company:
    #     return False
    # if not user or getattr(user, "role", None) != VirtualUserRoleSet.DEVICE:
    #     return False

    if not mapping.check_api_path(path):
        return False
    return True


def set_api_cache_data(company, path, ticket, result, headers):
    key = "API:{}".format(gen_key([path, company]))
    LOG.debug("company: {}".format(company))
    LOG.debug("key: {}".format(key))
    data = {
        "headers": headers,
        "result": result
    }
    LOG.info("ticket set: {}".format(ticket))
    set_api_data(key, data, ticket)


def format_final_tables(tables, code_map):
    data_tables = []
    for table in tables:
        name, level = table
        data_tables.append([name, level, code_map[level]])
    return data_tables


def _get_common_cache_data(key, data_tables):
    data = get_cache_data(key)
    if not data:
        return False, None

    ticket = data.get("ticket", None)
    info = data.get("data", None)
    LOG.info("ticket get: {}".format(ticket))

    values = get_tables_last_modify(data_tables)

    if not check_ticket(ticket, values):
        return False, None
    return True, info


def _set_common_cache_data(key, data, data_tables):
    values = get_tables_last_modify(data_tables)
    ticket = gen_ticket(values)
    LOG.info("ticket set: {}".format(ticket))
    set_cache_data(key, data, ticket)


def _dependant_cache_wrapper(_func, key_map, category, dependents):
    func_name = "{}.{}".format(_func.__module__, _func.__name__).upper()
    mapping.register(category, func=func_name, dependents=dependents, raise_exception=False)

    def wrapper(*args, **kwargs):
        tables = mapping.get_general_dependent_tables(func_name, category)
        code_map = {}
        for level, code_names in key_map.items():
            code_list = []
            for code_name in code_names:
                code_value = kwargs.get(code_name)
                if not code_value:
                    if level != LEVEL_ALL:
                        return _func(*args, **kwargs)
                    code_value = ""
                code_list.append("{}".format(code_value))
            if not code_list:
                return _func(*args, **kwargs)
            code_map[level] = gen_key(code_list)

        if not code_map:
            return _func(*args, **kwargs)

        key_list = ()
        if args:
            key_list += str(args),
        key_list += "##",
        if kwargs:
            key_list += str(kwargs),

        key = "{}:{}".format(category, gen_key((func_name, make_params_key(key_list))))
        data_tables = format_final_tables(tables, code_map)
        ret, result = _get_common_cache_data(key, data_tables)
        if not ret:
            LOG.info("miss {} cache: {}".format(func_name, key))
            try:
                result = _func(*args, **kwargs)
                if result:
                    _set_common_cache_data(key, result, data_tables)
            except Exception as e:
                LOG.error(e)
        else:
            LOG.info("hit {} cache: {}".format(func_name, key))
        return result

    return wrapper


def dependant_cache(key_map, dependents, category=CATEGORY_INNER):
    def decorating_function(_func):
        wrapper = _dependant_cache_wrapper(_func, key_map, category, dependents)
        return functools.update_wrapper(wrapper, _func)

    return decorating_function
