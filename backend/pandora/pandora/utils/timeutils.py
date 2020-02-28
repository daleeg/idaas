import time
import sys
import functools
import logging

LOG = logging.getLogger(__name__)


def current():
    if sys.platform == "win32":
        # On Windows, the best timer is time.clock()
        return time.clock()
    else:
        # On most other platforms the best timer is time.time()
        return time.time()


def time_it(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        start = current()
        ret = func(*args, **kwargs)
        LOG.info("Process {} Time: {}".format(func.__name__, current() - start))
        return ret
    return wrapped
