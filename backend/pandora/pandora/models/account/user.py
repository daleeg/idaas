# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, UnicodeUsernameValidator
from django.contrib.auth.hashers import make_password
from pandora.core.models.core import ExtraCoreModel
from pandora.core.models.manager import BaseQuerySet
from pandora.models.collection.user import UserRoleSet, UserGenderSet, USER_DEFAULT_PASSWORD

from pandora.utils.base64utils import base64_to_ori

__all__ = [
    "User",
]


class UserManager(BaseUserManager):
    use_in_migrations = True
    _queryset_class = BaseQuerySet

    def _create_user(self, username, password, direct, **extra_fields):
        """
        Creates and saves a User with the given username, password.
        """
        if not username:
            raise ValueError("The given username must be set")
        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        if not direct:
            user.set_password(password)
        else:
            user.password = password
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, direct=False, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, password, direct=direct, **extra_fields)

    def create_staffuser(self, username, password=None, direct=False, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, password, direct=direct, **extra_fields)

    def create_superuser(self, username, password, direct=False, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("name", username)
        extra_fields.setdefault("role", UserRoleSet.SUPERADMIN)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, password, direct=direct, **extra_fields)

    def get_queryset(self):
        """
        在这里处理一下QuerySet, 然后返回没被标记位is_deleted的QuerySet
        """
        kwargs = {"model": self.model, "using": self._db}
        if hasattr(self, "_hints"):
            kwargs["hints"] = self._hints
        return self._queryset_class(**kwargs).filter(is_deleted=False)


class User(AbstractBaseUser, ExtraCoreModel):
    username_validator = UnicodeUsernameValidator()
    name = models.CharField(max_length=128, blank=True, null=True, help_text=_("姓名"))
    description = models.TextField(blank=True, null=True, help_text=_("备注"))

    avatar = models.CharField(max_length=512, blank=True, null=True, help_text=_("头像"))
    gender = models.CharField(max_length=2, choices=UserGenderSet.choices(), default=UserGenderSet.MALE,
                              help_text=_("性别"))
    birthday = models.DateField(blank=True, null=True, help_text=_("生日"))
    email = models.EmailField(blank=True, null=True, help_text=_("邮箱"))
    phone = models.CharField(max_length=64, blank=True, null=True, help_text=_("电话"))

    role = models.CharField(max_length=32, choices=UserRoleSet.choices(), default=UserRoleSet.GENERAL,
                            help_text=_("角色"))

    username = models.CharField(_("username"), max_length=150, unique=True,
                                help_text=_("必填. 字符,数字和符号@/./+/-/_ ,最大长度150 "),
                                validators=[username_validator],
                                error_messages={
                                    "unique": _("用户名已经存在."),
                                }, )
    is_staff = models.BooleanField(_("staff status"), default=False,
                                   help_text=_("Designates whether the user can log into this admin site."), )
    is_active = models.BooleanField(_("active"), default=True,
                                    help_text=_("Designates whether this user should be treated as active. "
                                                "Unselect this instead of deleting accounts."), )
    is_superuser = models.BooleanField(_("superuser status"), default=False, help_text=_(
        "Designates that this user has all permissions without explicitly assigning them."), )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def __str__(self):
        return "{}: {}".format(self.name, str(self.username))

    def get_full_name(self):
        return "{}: {}".format(self.name, self.username)

    def get_short_name(self):
        return self.name

    def update_password(self, password, is_b64=False, company_id=None):
        if is_b64:
            password = base64_to_ori(password)
        self.set_password(password)
        self.save()

    @classmethod
    def make_password(cls, password, default=USER_DEFAULT_PASSWORD):
        if not password:
            return make_password(default)
        return make_password(password)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
