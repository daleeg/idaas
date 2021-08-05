# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.cache.backends.db import DatabaseCache
import logging

LOG = logging.getLogger(__name__)
db_cache = DatabaseCache("pandora_key_value", {})

