# -*- coding: utf-8 -*-
from django.utils.cache import caches
import logging

LOG = logging.getLogger(__name__)
INNER_CHANNELS = "default_idaas_channel"


class PublishClient(object):
    def __init__(self, channel=None):
        self.channel = INNER_CHANNELS if not channel else channel

    @property
    def redis(self):
        return self.client.get_client(write=True)

    @property
    def client(self):
        return caches["pub_sub"].client

    def publish(self, msg):
        self.redis.publish(self.channel, self.client.encode(msg))
        return True


class SubscribeServer(object):
    def __init__(self, channel=None):
        self.channel = INNER_CHANNELS if not channel else channel
        self.client = caches["pub_sub"].client
        self.redis = self.client.get_client(write=True)
        self.pub = self.redis.pubsub()
        self.pub.subscribe(self.channel)

    def subscribe(self, block=True, timeout=0):
        data = self.pub.parse_response(block, timeout)
        if not data:
            return None
        category, channel, message = data
        if category.decode() == "message":
            return self.client.decode(message)
        LOG.info(data)
        return None

    def subscribe_multi(self, count=0, block=False, timeout=0):
        result = []
        if count == 0:
            while True:
                data = self.subscribe(block, timeout)
                if not data:
                    break
                else:
                    result.append(data)
        else:
            for _ in range(count):
                data = self.subscribe(block, timeout)
                if not data:
                    break
                else:
                    result.append(data)
        return result

    def subscribe_all(self, block=False, timeout=0):
        return self.subscribe_multi(0, block, timeout)
