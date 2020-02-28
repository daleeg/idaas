#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from pandora.core.signal import app_broad

LOG = logging.getLogger(__name__)

__all__ = ["app_broad_handler", "app_broad_delete_handler", "app_broad_save_handler"]


@receiver(app_broad, dispatch_uid="my_signal_receiver")
def app_broad_handler(sender, **kwargs):
    pass


@receiver(post_delete)
def app_broad_delete_handler(sender, **kwargs):
    pass


@receiver(post_save)
def app_broad_save_handler(sender, **kwargs):
    pass
