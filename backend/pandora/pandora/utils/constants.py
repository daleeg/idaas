#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from collections import namedtuple

EVENT_LOGIN = 0x10
EVENT_LOGOUT = 0x11
EVENT_MODIFY = 0x12

EVENT_SHOW = {
    EVENT_LOGIN: u'Login',
    EVENT_LOGOUT: u'Logout',
    EVENT_MODIFY: u'modify self',
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
LOG_DIR = "/var/log/classboard/pandora"

POD = os.environ.get('POD_NAME')

if POD:
    LOG_FILE = "pandora_core_{}.log".format(POD)
else:
    LOG_FILE = "pandora_core.log"

AIDZBP_CEM = "AIDZBPCEM"  # AI智慧电子班牌环境监测
AIDZBP_FRA = "AIDZBPFRA"  # AI智慧电子班牌人脸识别考勤
AIDZBP_HC = "AIDZBPHC"  # AI智慧电子班牌运维监控
AIDZBPH_AS = "AIDZBPHAS"  # AI智慧电子班牌家校通微信小程序
AIDZBP_VA = "AIDZBPVA"  # AI智慧电子班牌语音小助手
AIDZBP_SSO = "AIDZBPSSO"  # AI智慧电子班牌统一认证
AIDZBP_CLASSBOARD = "AIDZBP-MAX-CLASSES"  # AI智慧电子班牌

CURRENT_LICENSE, APP_LICENSE, EXTRA_LICENSE, ALL_LICENSE = 0, 1, 2, 3
LICENSE_SHOW = [AIDZBP_CLASSBOARD, AIDZBP_CEM, AIDZBP_FRA, AIDZBP_VA]

DEFAULT_CLIENT_ID = "gjtxsjtyjsxqsl"
DEFAULT_CLIENT_SECRET = "Z2p0eHNqdHlqc3hxc2w="

LOG_MAX_SIZE = 100 * 1024 * 1024
LOG_BACKEUP_COUNT = 4

SHRINK_SUFFIX = "-thumbnail.jpg"
REPLICATION_TASK_CHANNEL = "replication_task_channel"
REPLICATION_TASK_QUEUE = "replication_task_queue"

Message = namedtuple('Message', ['code', 'action', 'model', 'param'])

UPGRADE_MODELS_CHANNEL = "upgrade_models_channel"
UPGRADE_MODELS_QUEUE = "upgrade_models_queue"
UpgradeMessage = namedtuple('UpgradeMessage', ['action', 'param', 'models'])

FLOW_ALL = "ALL"
FLOW_APP = "APP"

APPS = [FLOW_APP, FLOW_ALL]
ONE_DAY = 86400

ONLINE_INTERVAL = int(os.getenv("ONLINE_INTERVAL") or 10)

APP_DEFAULT_PWD = "qaz123wsxokm"
