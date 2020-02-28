# -*- coding: utf-8 -*-

from uuid import UUID


class ValuesWrapper(object):
    def __init__(self, instance, many_value=None, many=False):
        """
        用于结构化输出指定了查询字段的queryset
        :param instance:
        :param many_value: 深度为1的一对多关系匹配
        :param many:
        """
        self.instance = instance
        self.many_value = many_value if many_value else {}
        self.many = many

    def wrap(self, obj):
        data, value_fields = {}, list(obj.keys())
        for fields in value_fields:
            split_fields = fields.split("__")
            container = data
            for index, field in enumerate(split_fields):
                if index < len(split_fields) - 1:
                    if field not in container:
                        container[field] = {}
                    container = container[field]
                else:
                    container[field] = str(obj[fields]) if isinstance(obj[fields], UUID) else obj[fields]
        for key, value_map in self.many_value.items():
            data[key] = value_map[data['uid']]
        return data

    @property
    def data(self):
        data = [self.wrap(item) for item in self.instance] if self.many else self.wrap(self.instance)
        return data
