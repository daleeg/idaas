# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from functools import lru_cache
from collections import namedtuple
import re
from django.urls.resolvers import _route_to_regex as route_to_regex

LEVEL_ALL = 0
LEVEL_COMPANY = 1

LEVEL_SET = [
    LEVEL_ALL,
    LEVEL_COMPANY,
]

ITEM_CURRENT_DATE = "CurrentDate"

CATEGORY_INNER = "INNER"
CATEGORY_LINK = "LINK"
CATEGORY_API = "API"

REFRESH_EVERY_GET_ITEMS = [ITEM_CURRENT_DATE]

Node = namedtuple("Node", ("level", "item"))
Match = namedtuple("Match", ("route", "pattern", "compile"))


class Dependents(object):
    ALL = "__ALL__"

    def __init__(self):
        self.DEPENDENTS_MAP = {}
        self.DEPENDENTS_LEVEL_ITEM_MAP = {}
        self.TABLE_LEVELS = {}
        self.PATH_KEYS = []
        self.PATH_ROUTE_MAP = {}

    def get_dependants_all_items(self, keys=None):
        result = {k: [] for k in LEVEL_SET}
        if keys:
            keys = keys.split(",")
        else:
            keys = self.DEPENDENTS_MAP.keys()
        for key, tables in self.DEPENDENTS_MAP.items():
            if key not in keys:
                continue
            for level, table in tables:
                if table not in result[level]:
                    result[level].append(table)
        return result

    def set_path_key(self, route):
        named_path_components = []
        new_route = route.strip("/").split("/")
        for component in new_route:
            if "<" not in component:
                named_path_components.append(component)
                if component not in self.PATH_KEYS:
                    self.PATH_KEYS.append(component)
        path_key = "_".join(named_path_components)
        new_route_len = len(new_route)
        self.PATH_ROUTE_MAP.setdefault(new_route_len, {})
        len_path_routes = self.PATH_ROUTE_MAP[new_route_len]
        len_path_routes.setdefault(path_key, [])
        len_path_routes.setdefault(self.ALL, [])

        regex_route, _ = route_to_regex(route)
        match = Match(route=route, pattern=regex_route, compile=re.compile(regex_route))

        for key in [path_key, self.ALL]:
            path_routes = len_path_routes[key]
            if route not in path_routes:
                path_routes.append(match)

    def match_path(self, path):
        named_path_components = []
        new_path = path.strip("/").split("/")
        new_route_len = len(new_path)
        len_path_routes = self.PATH_ROUTE_MAP.get(new_route_len, {})
        if not len_path_routes:
            return False
        for component in new_path:
            if component in self.PATH_KEYS:
                named_path_components.append(component)

        path_key = "_".join(named_path_components)
        for key in [path_key, self.ALL]:
            path_routes = len_path_routes.get(key, [])
            for match in path_routes:
                m = re.match(match.compile, path)
                if m:
                    return match.route

        return False

    def register(self, category=CATEGORY_API, func=None, route=None, dependents=[], raise_exception=True):
        if category == CATEGORY_API:
            assert route, "API注册需要route参数"
            route = route.lower()
            self.set_path_key(route)
            key = "{}:{}".format(category, route)
        else:
            func = func.upper()
            key = "{}:{}".format(category, func)
        if key in self.DEPENDENTS_MAP:
            if raise_exception:
                raise Exception("API {}".format(route) if category == CATEGORY_API else "函数{}".format(func) + "已经被注册")
            else:
                return
        items = []
        level_item = {}
        for dependent in dependents:
            level = dependent.level
            level_item.setdefault(level, [])
            assert level in LEVEL_SET, "level-{}的类型不支持,{}".format(level, LEVEL_SET)
            for item in dependent.item:
                self.TABLE_LEVELS.setdefault(item, [])
                table_level = self.TABLE_LEVELS[item]
                if item not in table_level:
                    table_level.append(level)
                items.append([item, level])
                level_item[level].append(item)

        self.DEPENDENTS_LEVEL_ITEM_MAP[key] = level_item
        self.DEPENDENTS_MAP[key] = items
        self.get_api_company_dependent_tables.cache_clear()

    def get_api_dependent_tables(self, path):
        route = self.match_path(path)
        key = "{}:{}".format(CATEGORY_API, route)
        return self.DEPENDENTS_MAP.get(key, [])

    def check_api_path(self, path):
        route = self.match_path(path)
        key = "{}:{}".format(CATEGORY_API, route)
        return key in self.DEPENDENTS_MAP

    @lru_cache(maxsize=65536)
    def get_api_company_dependent_tables(self, company_id, path, ):
        tables = self.get_api_dependent_tables(path)
        data_tables = []
        for table in tables:
            name, level = table
            if level == LEVEL_ALL:
                data_tables.append([name, level, ""])
            elif level == LEVEL_COMPANY:
                data_tables.append([name, level, company_id])
        return data_tables

    def get_link_dependent_tables(self, key):
        key = "{}:{}".format(CATEGORY_LINK, key)
        return self.DEPENDENTS_MAP.get(key, [])

    def get_inner_dependent_tables(self, key):
        key = "{}:{}".format(CATEGORY_INNER, key)
        return self.DEPENDENTS_MAP.get(key, [])

    def get_general_dependent_tables(self, key, category):
        if category != CATEGORY_API:
            key = "{}:{}".format(category, key)
        return self.DEPENDENTS_MAP.get(key, [])

    def get_dependent_items(self, keys):
        all_items = self.get_dependants_all_items(",".join(keys))
        return all_items

    @property
    def api_keys(self):
        return [key for key in self.DEPENDENTS_MAP.keys() if key.startswith(CATEGORY_API)]

    def get_general_dependent_tables(self, key, category):
        if category != CATEGORY_API:
            key = "{}:{}".format(category, key)
        return self.DEPENDENTS_MAP.get(key, [])

    def get_table_levels(self, table):
        return self.TABLE_LEVELS.get(table, [])
