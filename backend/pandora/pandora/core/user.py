from django.contrib.auth.models import AnonymousUser
from pandora.utils.keyvalue_utils import get_virth_users
from pandora.models import VirtualUserRoleSet


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


class VirthSuperUser(AnonymousUser):
    is_active = True
    is_auth = False
    role = VirtualUserRoleSet.SUPPER

    def __init__(self, client_id):
        self.username = client_id
        self.last_name = client_id

    def __str__(self):
        return 'VirthSuperUser:{}'.format(self.username)

    def check_password(self, raw_password):
        users = get_virth_users()
        client_secret = users.get(self.username, None)
        if client_secret and client_secret == raw_password:
            self.is_auth = True
            self.is_staff = True
            self.is_superuser = True
            return True
        return False

    @property
    def is_authenticated(self):
        return self.is_auth
