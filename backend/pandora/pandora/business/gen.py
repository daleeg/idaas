# -*- coding: utf-8 -*-
import os
import binascii


def generate_unique_code(model, prefix="", look_up="code"):
    code = None
    for _ in range(100):
        code = "{}{}".format(prefix, binascii.hexlify(os.urandom(8)).decode())
        try:
            model.objects.get(**{look_up: code})
        except model.DoesNotExist:
            return code
    return code
