# -*- coding: utf-8 -*-
from django.utils.cache import caches
import logging

LOG = logging.getLogger(__name__)
INNER_QUEUE = "default_pandora_queue"


class RedisQueue(object):
    def __init__(self, queue=None):
        self._queue_name = "queue:{}".format(queue or INNER_QUEUE)

    @property
    def redis(self):
        return self.client.get_client(write=True)

    @property
    def client(self):
        return caches["queue"].client

    def enq(self, data, parser=None):
        if parser and callable(parser):
            data = parser(data)
        self.redis.rpush(self._queue_name, self.client.encode(data))
        return True

    def deq_all(self, parser=None):
        return self.deq_multi(count=0, parser=parser)

    def deq_multi(self, count=0, parser=None):
        """
        Retrieves and removes the all oldest item from the queue
        """
        length = self.length
        length = count if 0 < count < length else length
        result = []
        if parser and callable(parser):
            for _ in range(length):
                message = self.redis.lpop(self._queue_name)
                try:
                    data = self.client.decode(message)
                    data = parser(data)
                    result.append(data)
                except:
                    pass
        else:
            for _ in range(length):
                message = self.redis.lpop(self._queue_name)
                try:
                    data = self.client.decode(message)
                    result.append(data)
                except:
                    pass
        return result

    def deq(self, parser=None):
        """
        Retrieves and removes the oldest item from the queue
        """
        message = self.redis.lpop(self._queue_name)
        data = self.client.decode(message)
        if parser and callable(parser):
            data = parser(data)
        return data

    @property
    def length(self):
        return self.redis.llen(self._queue_name)
