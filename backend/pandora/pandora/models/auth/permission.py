#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pandora.models.base import ExtraCoreModel, ExtraBaseModel
from django.db import models
from django.utils.translation import ugettext_lazy as _
from pandora.models.collection import DataOriginSet, GroupPermissionLevel
from mptt.models import TreeForeignKey
from pandora.models.base import MpttExtraCoreModel
from pandora.models.collection import CommonStatus, TerminalCategory, ActionMode
from pandora.models.account import User

__all__ = [
    "Menu",
    "Module",
    "CatalogPermissionGroup",
    "CatalogPermissionGroupMember",
    "CatalogPermissionGroupMenu",
    "CatalogPermissionGroupModule",
]


class Menu(MpttExtraCoreModel):
    client_id = models.CharField(help_text=_("项目标签"), max_length=100)
    alias = models.CharField(help_text=_("模块英文名称"), max_length=64)
    name = models.CharField(max_length=32, db_index=True, help_text=_("名称"))
    code = models.CharField(max_length=32, db_index=True, help_text=_("编码"))
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, related_name="children",
                            help_text=_("父节点"), db_constraint=False)
    terminals = models.IntegerField(default=TerminalCategory.none(), help_text=_(TerminalCategory.message()))
    description = models.TextField(help_text=_("简介"), blank=True, null=True)
    category = models.CharField(max_length=20, default="menu")
    status = models.IntegerField(default=CommonStatus.ENABLE, help_text=_(CommonStatus.message()))
    mode = models.IntegerField(default=ActionMode.all(), help_text=(ActionMode.message()))
    sort_number = models.IntegerField(blank=True, null=True, help_text=_("显示排序值"))

    class MPTTMeta:
        order_insertion_by = ["name"]


class Module(ExtraCoreModel):
    client_id = models.CharField(help_text=_("项目标签"), max_length=100)
    alias = models.CharField(help_text=_("模块英文名称"), max_length=64)
    code = models.CharField(help_text=_("模块编码"), max_length=64)
    name = models.CharField(help_text=_("模块中文名称"), max_length=255)
    terminals = models.IntegerField(default=TerminalCategory.none(), help_text=_(TerminalCategory.message()))
    menu = models.ForeignKey(Menu, on_delete=models.SET_NULL, null=True,
                             related_name="module", help_text=_("菜单"), db_constraint=False)
    category = models.CharField(max_length=20, default="module")
    status = models.IntegerField(default=CommonStatus.ENABLE, help_text=_(CommonStatus.message()))
    mode = models.IntegerField(default=ActionMode.all(), help_text=(ActionMode.message()))
    description = models.TextField(help_text=_("简介"), blank=True, null=True)
    sort_number = models.IntegerField(blank=True, null=True, help_text=_("显示排序值"))


class CatalogPermissionGroup(ExtraBaseModel):
    client_id = models.CharField(help_text=_("项目标签"), max_length=100)
    name = models.CharField(help_text=_("组中文名称"), max_length=255)
    code = models.CharField(help_text=_("操作权限编码"), blank=True, null=True, max_length=64)
    description = models.CharField(help_text=_("简介"), max_length=255, blank=True, null=True)
    category = models.SmallIntegerField(help_text=_("组权限类型, {}".format(DataOriginSet.message())),
                                        default=DataOriginSet.SELF)
    status = models.IntegerField(default=CommonStatus.DISABLE, help_text=_(CommonStatus.message()))
    level = models.SmallIntegerField(help_text=_("组权限数据级别".format(GroupPermissionLevel.message())),
                                     default=GroupPermissionLevel.LEVEL_PERSON)


class CatalogPermissionGroupMember(ExtraBaseModel):
    group = models.ForeignKey(CatalogPermissionGroup, to_field="uid", help_text=_("组, uid"),
                              related_name="catalog_member_user",
                              on_delete=models.CASCADE, null=True, db_constraint=False)
    user = models.ForeignKey(User, to_field="uid", help_text=_("用户, uid"), related_name="catalog_member_group",
                             on_delete=models.CASCADE, null=True, db_constraint=False)


class CatalogPermissionGroupMenu(ExtraBaseModel):
    group = models.ForeignKey(CatalogPermissionGroup, to_field="uid", help_text=_("组, uid"),
                              related_name="group_menu",
                              on_delete=models.CASCADE, null=True, db_constraint=False)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True,
                             related_name="menu_group", help_text=_("菜单"), db_constraint=False)
    mode = models.IntegerField(default=ActionMode.none(), help_text=(ActionMode.message()))


class CatalogPermissionGroupModule(ExtraBaseModel):
    group = models.ForeignKey(CatalogPermissionGroup, to_field="uid", help_text=_("组, uid"),
                              related_name="group_module",
                              on_delete=models.CASCADE,  null=True, db_constraint=False)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, null=True,
                               related_name="module_group", help_text=_("模块"), db_constraint=False)
    mode = models.IntegerField(default=ActionMode.none(), help_text=(ActionMode.message()))
