# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from collections import namedtuple

InnerMessage = namedtuple("Message", ["table", "event", "body"])
