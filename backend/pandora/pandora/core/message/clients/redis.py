# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from pandora.utils.channel import PublishClient
import logging

LOG = logging.getLogger(__name__)


class MessageClient(object):
    def __init__(self):
        self.pub = PublishClient()

    def send_push(self, message):
        LOG.debug(message)
        self.pub.publish(message)


message_client = MessageClient()
