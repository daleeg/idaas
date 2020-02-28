import os
from base64 import b64decode, b64encode
from zlib import decompress

try:
    # cpython 2.x
    from cPickle import loads, dumps  # noqa
except ImportError:
    from pickle import loads, dumps  # noqa


def base64_to_jpg(content, path, name):
    imgdata = b64decode(content)
    jpg_path = os.path.join(path, name)
    with open(jpg_path, 'wb') as file:
        file.write(imgdata)
    return jpg_path


def base64_to_file(content, path, name):
    data = b64decode(content)
    path = os.path.join(path, name, )
    with open(path, 'wb') as file:
        file.write(data)
    return path


def base64_from_file(file_name):
    with open(file_name, 'rb') as file:
        content = file.read()
    if content:
        result = b64encode(content)
    else:
        result = None
    return result


def dbsafe_decode(value, compress_object=False):
    if not value:
        return None
    value = value.encode()  # encode str to bytes
    value = b64decode(value)
    if compress_object:
        value = decompress(value)
    return loads(value)
