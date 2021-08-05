# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import inspect
import operator
from rest_framework.permissions import BasePermission
from pandora.models.collection import UserRoleSet


class GroupPermission(BasePermission):
    """
    通过定义permission_classes_groups来实现or方式的验证
    permission_classes_groups = [(permission_classes1), (permission_classes2)]
    permission_classes1和permission_classes2只要有一个为True则具有访问权限
    """

    def __init__(self):
        self.message = None

    def has_permission(self, request, view):
        permission_groups = getattr(view, 'permission_classes_groups', [])
        for permission_group in permission_groups:
            ret, message = self.check_permission_group(permission_group, request, view)
            if ret:
                self.message = None
                return True

        self.message = message
        return False

    def check_permission_group(self, permissions, request, view):
        if isinstance(permissions, list) or isinstance(permissions, tuple):
            for permission in permissions:
                if not permission().has_permission(request, view):
                    message = getattr(permission, 'message', None)
                    return False, message

        return True, None


class OpBasePermission(BasePermission):
    def __init__(self, *args):
        self.components = [c() if inspect.isclass(c) else c for c in args]

    def __call__(self):
        return self


class And(OpBasePermission):
    def has_permission(self, request, view):
        result = True
        for component in self.components:
            result = operator.iand(result, component.has_permission(request, view))
        return result


class Or(OpBasePermission):
    def has_permission(self, request, view):
        result = False
        for component in self.components:
            result = operator.ior(result, component.has_permission(request, view))
        return result


class Not(OpBasePermission):
    def __init__(self, *args):
        self.components = [c() if inspect.isclass(c) else c for c in args]
        assert len(self.components) == 1, "must single params"

    def has_permission(self, request, view):
        return not self.components[0].has_permission(request, view)


class SuperuserPermission(BasePermission):
    """Allow access only to superuser"""

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class StaffPermission(BasePermission):
    """Allow access to superuser and staff"""

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class ActivePermission(BasePermission):
    """Allow access to superuser and staff, exclude developer"""

    def has_permission(self, request, view):
        user_role = getattr(request.user, "role", None) if request.user else None
        return request.user and request.user.is_active and user_role != UserRoleSet.DEVELOPER


class CompanyPermission(BasePermission):
    """Allow access to superuser and staff"""

    def has_permission(self, request, view):
        return request.company


class DeveloperPermission(BasePermission):
    """Allow access to developer"""

    def has_permission(self, request, view):
        user_role = getattr(request.user, "role", None) if request.user else None
        return request.user and request.user.is_active and user_role == UserRoleSet.DEVELOPER
