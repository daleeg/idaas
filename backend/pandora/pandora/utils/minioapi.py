#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import logging
import sys
import os
from minio import Minio
from minio.error import ResponseError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
DEFAULT_BULK = "log"
# from pandora.models.idaas.schedule import PeriodSet

LOG = logging.getLogger(__name__)


def get_minio_url_base():
    host = os.environ.get("MINIO_HOST", "ischool.h3c.com")
    port = os.environ.get("MINIO_PORT", 17467)
    url = "{}:{}".format(host, port)
    return url


def get_operation_center_secret():
    client_id = os.environ.get("MINIO_CLIENT_ID", "app")
    client_secret = os.environ.get("MINIO_CLIENT_SECRET", "ischool@h3c.com")
    return client_id, client_secret


class MinioApi(object):
    def __init__(self, client=None, base_url=None):
        if not base_url:
            self._base_url = get_minio_url_base()
        else:
            self._base_url = base_url

        if not client:
            self._client_id, self._client_secret = get_operation_center_secret()
        else:
            self._client_id, self._client_secret = client
        self.client = Minio(self._base_url, access_key=self._client_id,
                            secret_key=self._client_secret, secure=False)

    def get_default_bulk(self):
        bulk = DEFAULT_BULK
        try:
            ret = self.client.bucket_exists(bulk)
            if not ret:
                self.client.make_bucket(bulk)
        except ResponseError as err:
            LOG.error(err)
            raise
        return bulk

    def upload_file(self, name, trunk_file, length):
        bulk = self.get_default_bulk()
        try:
            ret = self.client.put_object(bulk, name, trunk_file, length)
        except ResponseError as err:
            LOG.error(err)
            raise
        return ret


minio_api = MinioApi()
