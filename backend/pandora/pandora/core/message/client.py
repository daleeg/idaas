# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from pandora.core.message.clients import redis

__all__ = ["message_client"]

message_client = redis.message_client
