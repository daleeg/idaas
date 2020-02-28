from pandora.core.models import BaseSet
from django.utils.translation import ugettext_lazy as _

__all__ = [
    'UserRoleSet',
    'VirtualUserRoleSet',

]


class UserRoleSet(BaseSet):
    ADMIN = 0
    TEACHER = 1
    STUDENT = 2
    GUEST = 3

    MESSAGE = {
        STUDENT: _("学生"),
        TEACHER: _("老师"),
        ADMIN: _("管理员"),
        GUEST: _("访客")
    }


class VirtualUserRoleSet(BaseSet):
    DEVICE = 11
    SUPPER = 12

    MESSAGE = {
        DEVICE: _("设备"),
        SUPPER: _("超级用户"),
    }
