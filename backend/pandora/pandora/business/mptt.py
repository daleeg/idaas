# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


def manage_tree(nodes, key="uid"):
    root_list = []
    node_map = {n[key]: n for n in nodes}
    for n in nodes:
        parent_id = n["parent_id"]
        if parent_id in node_map:
            parent = node_map[parent_id]
            if "children" not in parent:
                parent["children"] = []
            parent["children"].append(n)
        else:
            root_list.append(n)
    return root_list
