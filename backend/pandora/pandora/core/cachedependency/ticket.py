# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import hashlib


def gen_ticket(values):
    ticket_str = ",".join(values)
    return hashlib.md5(ticket_str.encode(encoding="utf8")).hexdigest()


def gen_key(values):
    values = ["{}".format(v) for v in values]
    key_str = "_".join(values)
    return key_str
    # return hashlib.md5(key_str.encode(encoding="utf8")).hexdigest()


def make_params_key(values):
    values = ["{}".format(v) for v in values]
    key_str = "_".join(values)
    return hashlib.md5(key_str.encode(encoding="utf8")).hexdigest()


def check_ticket(ticket, values):
    return ticket == gen_ticket(values)
