from __future__ import absolute_import, unicode_literals

from django.db import models, transaction


__all__ = [
    "Token",
]
import binascii
import os

from pandora.models.base import ExtraCoreModel
from pandora.models.account import User
from django.utils.translation import gettext_lazy as _


class Token(ExtraCoreModel):
    """
    The default authorization token model.
    """
    key = models.CharField(_("Key"), max_length=40, db_index=True)

    browser = models.CharField(null=True, blank=True, max_length=20)
    os = models.CharField(null=True, blank=True, max_length=20)
    platform = models.CharField(null=True, blank=True, max_length=20)
    remote_ip = models.GenericIPAddressField(null=True, blank=True)

    user = models.ForeignKey(User, related_name='token', on_delete=models.CASCADE, verbose_name=_("User"), null=True,
                             db_constraint=False)

    class Meta:
        # Work around for a bug in Django:
        # https://code.djangoproject.com/ticket/19422
        #
        # Also see corresponding ticket:
        # https://github.com/encode/django-rest-framework/issues/705
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
