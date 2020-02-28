# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import functools
from django.core.cache import caches
from django.utils import timezone
import logging

LOG = logging.getLogger(__name__)
lock_flag = True

cache = caches["distributed_lock"]


class DistributedLockError(Exception):
    pass


def distributed_lock(lock_name=None, expire=60, blocking=False, timeout=None):
    def decorating_function(func):
        wrapper = _distributed_lock_wrapper(func, lock_name, expire, blocking, timeout)
        return functools.update_wrapper(wrapper, func)

    return decorating_function


def _distributed_lock_wrapper(func, lock_name, expire, blocking, timeout):
    if not lock_name:
        lock_name = "distributed_lock_{}".format(func.__name__)
    else:
        lock_name = "distributed_lock_{}".format(lock_name)

    if lock_flag:
        def wrapper(*args, **kwargs):
            _lock = cache.lock(lock_name, expire=expire, auto_renewal=True)
            if _lock.acquire(blocking=blocking, timeout=timeout):
                LOG.info("Got the lock - {}".format(lock_name))
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    LOG.info(e)
                    raise
                finally:
                    LOG.info("Release the lock - {}".format(lock_name))
                    _lock.release()
            else:
                LOG.info("Someone else has the lock - {}".format(lock_name))
                raise DistributedLockError("Someone else has the lock - {}".format(lock_name))

        return wrapper

    else:
        return func


class DistributedLock(object):
    def __init__(self, lock_name=None, expire=60, blocking=False, timeout=None):
        if not lock_name:
            self.lock_name = "DL_{}".format(timezone.now().timestamp())
        else:
            self.lock_name = "DL_{}".format(lock_name)
        self.blocking = blocking
        self.timeout = timeout
        self._lock = cache.lock(lock_name, expire=expire, auto_renewal=True)

    def __enter__(self):
        acquired = self._lock.acquire(blocking=self.blocking, timeout=self.timeout)
        if acquired:
            LOG.info("Got the lock - {}".format(self.lock_name))
        else:
            DistributedLockError("Someone else has the lock - {}".format(self.lock_name))
        return self._lock

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        self._lock.release()
        LOG.info("Release the lock - {}".format(self.lock_name))
