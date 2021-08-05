from django.contrib.auth.models import AnonymousUser
from pandora.models.collection import CommonStatus, VirtualUserRoleSet, InterfacePermissionSet
from pandora.business.base import get_object_info


class DeviceUser(AnonymousUser):
    is_active = True
    role = VirtualUserRoleSet.DEVICE

    def __init__(self, name):
        self.username = name
        self.last_name = name

    def __str__(self):
        return 'DeviceUser:{}'.format(self.username)

    @property
    def is_authenticated(self):
        return True


class ClientUser(AnonymousUser):
    is_active = True
    is_auth = False
    role = VirtualUserRoleSet.CLIENT

    def __init__(self, client_id):
        self.username = client_id
        self.last_name = client_id

    def __str__(self):
        return 'App Client User:{}'.format(self.username)

    def check_password(self, raw_password):
        return True

    def auto_pass_authenticated(self):
        self.is_auth = True
        self.is_staff = True
        self.is_superuser = True

    @property
    def is_authenticated(self):
        return self.is_auth

