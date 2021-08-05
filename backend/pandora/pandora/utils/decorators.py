import time
import sys
import functools
import logging
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema as _swagger_auto_schema
from drf_yasg.utils import unset
from rest_framework.decorators import action as _action

LOG = logging.getLogger(__name__)

__all__ = [
    "time_it",
    "action",
    "swagger_auto_schema"
]

# swagger_auto_schema = _swagger_auto_schema
action = _action


def action(methods=None, detail=None, url_path=None, url_name=None, many=False, **kwargs):
    def decorator(view_method):
        view_method = _action(methods, detail, url_path, url_name, **kwargs)(view_method)
        view_method.many = many
        return view_method
    return decorator


def swagger_auto_schema(auto_schema=unset, response_body=None, **kwargs):

    def decorator(view_method):
        if settings.DEBUG:
            view_method = _swagger_auto_schema(auto_schema=auto_schema, **kwargs)(view_method)
            if response_body:
                existing_data = getattr(view_method, "_swagger_auto_schema", {})
                existing_data["response_body"] = response_body

        return view_method

    return decorator


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
