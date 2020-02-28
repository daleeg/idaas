# import gevent
# from gevent import monkey
# from gevent.pool import Pool
import logging

LOG = logging.getLogger(__name__)

MAX_COUNT = 10


# monkey.patch_all(thread=False)


def batch(func, params=None, step=1):
    # new_params = [params[i:i + step] for i in range(0, len(params), step)]
    # LOG.info(new_params)
    params = params or []

    def _coroutine(_params):
        _result = []
        for _param in _params:
            try:
                LOG.debug("{}---{}".format(func.__name__, _param))
                if isinstance(_param, dict):
                    ret = func(**_param)
                elif isinstance(_param, list) or isinstance(_param, tuple):
                    ret = func(*_param)
                else:
                    ret = "error param type:{}".format(_param)
            except Exception as e:
                LOG.error(e)
                ret = "{}".format(e)
            _result.append(ret)
        return _result

    # pool = Pool(MAX_COUNT)
    # tasks = [pool.spawn(_coroutine, param) for param in new_params]
    # gevent.joinall(tasks)
    # result = []
    # for task in tasks:
    #     value = task.value
    #     if isinstance(value, list):
    #         result.extend(task.value)
    result = _coroutine(params)
    return result
