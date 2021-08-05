#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from pandora.core.signal import message_channel
from pandora.utils.cacheutils import delete_object_info_cache
from pandora.core.cachedependency import client
from pandora.core.message import InnerMessage
from pandora.core.message.client import message_client
from pandora.utils.common import tohex

LOG = logging.getLogger(__name__)

__all__ = ["message_channel_handler", "app_broad_delete_handler", "app_broad_save_handler"]


# app_board.send(sender=ExamClassroom, instance=None, table="ExamClassroom", event="modify")
@receiver(message_channel, dispatch_uid="auto_signal_receiver")
def message_channel_handler(sender, instance, table, event, body, **kwargs):
    message = InnerMessage(table=table, event=event, body=body)
    message_client.send_push(message._asdict())


@receiver(post_delete)
def app_broad_delete_handler(sender, instance, signal, *args, **kwargs):
    mode_name = instance.__class__.__name__
    uid = getattr(instance, "uid", None)
    if uid:
        delete_object_info_cache(mode_name, tohex(instance.uid))

    client_id = getattr(instance, "client_id", None)
    if client_id:
        delete_object_info_cache(mode_name, instance.client_id)

    table = instance.__class__.__name__
    client.refresh_table_dependency(table, instance)
    # event = message_event.DELETE
    # body = get_object_info(instance._meta.model, instance.pk, field="pk")
    # message = InnerMessage(table=table, event=event, body=body)
    # message_client.send_push(message._asdict())


@receiver(post_save)
def app_broad_save_handler(sender, instance, signal, *args, **kwargs):
    mode_name = instance.__class__.__name__
    uid = getattr(instance, "uid", None)
    if uid:
        delete_object_info_cache(mode_name, tohex(instance.uid))

    client_id = getattr(instance, "client_id", None)
    if client_id:
        delete_object_info_cache(mode_name, instance.client_id)

    table = instance.__class__.__name__
    client.refresh_table_dependency(table, instance)

    # if kwargs["created"]:
    #     event = message_event.ADD
    # else:
    #     if hasattr(instance, "is_deleted"):
    #         is_deleted = getattr(instance, "is_deleted")
    #     else:
    #         is_deleted = False
    #     if not is_deleted:
    #         event = message_event.MODIFY
    #     else:
    #         event = message_event.DELETE
    #
    # body = get_object_info(instance._meta.model, instance.pk, field="pk")
    # message = InnerMessage(table=table, event=event, body=body)
    # message_client.send_push(message._asdict())
