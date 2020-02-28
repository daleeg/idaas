from django.db import connection
import time


def is_connection_usable():
    try:
        connection.connection.ping()
    except:
        return False
    else:
        return True


def connection_protect(func):

    def wrapper(*args, **kwargs):
        if not is_connection_usable():
            connection.close()
        try:
            return func(*args, **kwargs)
        except (Exception,) as e:
            time.sleep(1)
            raise
    return wrapper
