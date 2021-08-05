#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from collections import namedtuple

EVENT_LOGIN = 0x10
EVENT_LOGOUT = 0x11
EVENT_MODIFY = 0x12

EVENT_SHOW = {
    EVENT_LOGIN: u"Login",
    EVENT_LOGOUT: u"Logout",
    EVENT_MODIFY: u"modify self",
}

all_images = ["JPEG", "PNG"]
ext_map = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "TXT": ".txt",
    "INI": ".ini",
    "JSON": ".json",
    "MP4": ".mp4",
}
max_image_size = 5242880

FILE_LOG_LEVEL = logging.INFO
CONSOLE_LOG_LEVEL = logging.INFO
LOG_DIR = "/var/log/idaasctl/pandora"

POD = os.environ.get("POD_NAME")
if POD:
    LOG_FILE = "pandora_core_{}.log".format(POD)
else:
    LOG_FILE = "pandora_core.log"



LOG_MAX_SIZE = 100 * 1024 * 1024
LOG_BACKEUP_COUNT = 4

SHRINK_SUFFIX = "-thumbnail.jpg"
REPLICATION_TASK_CHANNEL = "replication_task_channel"
REPLICATION_TASK_QUEUE = "replication_task_queue"

Message = namedtuple("Message", ["code", "action", "model", "param"])

ONE_DAY = 86400

ONLINE_INTERVAL = int(os.getenv("ONLINE_INTERVAL") or 10)
