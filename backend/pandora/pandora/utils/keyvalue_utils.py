# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.cache.backends.db import DatabaseCache
from functools import lru_cache
from nirvana.utils.seiueutils import SeiueApi
import nirvana.utils.constants as cst
import os
import logging

LOG = logging.getLogger(__name__)
db_cache = DatabaseCache("nirvana_key_value", {})


def set_site_info(school, info):
    key = 'SITE_INFO:{}'.format(school)
    value = db_cache.get(key)
    if value and value.get('city') == info['city'] and value.get('province') == info['province']:
        if not info['ADCode'] or value.get('ADCode') == info['ADCode']:
            return False
    db_cache.set(key, info, timeout=None)
    return True


def get_site_info(school):
    key = 'SITE_INFO:{}'.format(school)
    value = db_cache.get(key)
    if value is None:
        value = {
            'province': None,
            'city': None,
            'ADCode': None
        }
        old_key = 'SITE_INFO'
        value = db_cache.get(old_key, value)
        db_cache.delete(old_key)
        db_cache.set(key, value, timeout=None)
    return value


def delete_site_info(school):
    key = 'SITE_INFO:{}'.format(school)
    db_cache.delete(key)


def get_switch_time(school):
    key = 'SWITCH_TIME:{}'.format(school)
    value = db_cache.get(key)
    if not value:
        value = {
            'on_time': None,
            'off_time': None,
        }
        old_key = 'SWITCH_TIME'
        value = db_cache.get(old_key, value)
        db_cache.delete(old_key)
        db_cache.set(key, value, timeout=None)

    return value


def set_switch_time(school, switch_time):
    key = 'SWITCH_TIME:{}'.format(school)
    db_cache.set(key, switch_time, timeout=None)
    # _send_switch_time()


def delete_switch_time(school):
    key = 'SWITCH_TIME:{}'.format(school)
    db_cache.set(key, None, timeout=None)
    # _send_switch_time()


def get_skin(school):
    key = 'SKIN:{}'.format(school)
    value = db_cache.get(key)
    if not value:
        value = {'skin': 0, 'mode': 0}
        old_key = 'SKIN'
        value = db_cache.get(old_key, value)
        db_cache.delete(old_key)
        db_cache.set(key, value, timeout=None)
    skin_none = value.get('skin') is None
    mode_none = value.get('mode') is None
    if skin_none or mode_none:
        value['skin'] = 0 if skin_none else value['skin']
        value['mode'] = 0 if mode_none else value['mode']
        db_cache.set(key, value, timeout=None)
    return value


def set_skin(school, skin):
    key = 'SKIN:{}'.format(school)
    db_cache.set(key, skin, timeout=None)


def delete_skin(school):
    key = 'SKIN:{}'.format(school)
    db_cache.set(key, None, timeout=None)


def get_mode(school):
    key = 'MODE:{}'.format(school)
    value = db_cache.get(key)
    if not value:
        value = 0
        old_key = 'MODE'
        value = db_cache.get(old_key, value)
        db_cache.delete(old_key)
        db_cache.set(key, value, timeout=None)
    return value


def set_mode(school, mode):
    key = 'MODE:{}'.format(school)
    db_cache.set(key, mode, timeout=None)


def get_face_server(school):
    key = 'FACE_SERVER:{}'.format(school)
    value = db_cache.get(key)
    if not value:
        value = {
            "enable": False,
            "ip": os.environ.get('ZMQ_FACE_SERVER', '127.0.0.1'),
            "port": int(os.environ.get('ZMQ_FACE_PORT', 23456))
        }
        old_key = 'FACE_SERVER'
        value = db_cache.get(old_key, value)
        db_cache.delete(old_key)
        db_cache.set(key, value, timeout=None)
    return value


def set_face_server(school, server_info):
    key = 'FACE_SERVER:{}'.format(school)
    db_cache.set(key, server_info, timeout=None)


def get_app_upgrade_server():
    key = 'APP_UPGRADE_SERVER'
    value = db_cache.get(key)
    if not value:
        value = {
            "host": os.environ.get("APP_UPGRADE_SERVER", "ischool.h3c.com"),
            "port": int(os.environ.get("APP_UPGRADE_PORT", 5010)),
        }
        db_cache.set(key, value, timeout=None)
    return value


def set_app_upgrade_server(server_info):
    key = 'APP_UPGRADE_SERVER'
    db_cache.set(key, server_info, timeout=None)


def get_custom_items(school):
    key = 'CUSTOM_ITEMS:{}'.format(school)
    value = db_cache.get(key)
    if not value:
        value = {
            'custom_items': [4, 3]
        }
        old_key = 'CUSTOM_ITEMS'
        value = db_cache.get(old_key, value)
        db_cache.delete(old_key)
        db_cache.set(key, value, timeout=None)
    return value


def set_custom_items(school, items):
    key = 'CUSTOM_ITEMS:{}'.format(school)
    db_cache.set(key, items, timeout=None)


def delete_custom_items(school):
    key = 'CUSTOM_ITEMS:{}'.format(school)
    db_cache.set(key, None, timeout=None)


@lru_cache()
def _get_seiue_client(school):
    seiue_info = get_seiue_info(school)
    client_id = seiue_info.get("client_id", None)
    client_secret = seiue_info.get("client_secret", None)
    school_id = seiue_info.get("school_id", None)
    seiue_url = seiue_info.get("seiue_url", "https://open.seiue.com")
    prefix = seiue_info.get("prefix", "/api/v1/")

    if client_id and client_secret and school_id and seiue_url and prefix:
        return SeiueApi(school_id, client_id, client_secret, seiue_url, prefix)
    return None


def get_seiue_client(school):
    client = _get_seiue_client(school)
    if not client:
        _get_seiue_client.cache_clear()
    return client


def get_seiue_info(school):
    key = 'SEIUE:{}'.format(school)
    value = db_cache.get(key)
    if not value:
        value = {
            "client_id": None,
            "client_secret": None,
            "school_id": None,
            "seiue_url": "https://open.seiue.com",
            "prefix": "/api/v1/"
        }
        old_key = 'SEIUE'
        value = db_cache.get(old_key, value)
        db_cache.delete(old_key)
        set_seiue_info(school, value)
    return value


def set_seiue_info(school, info):
    key = 'SEIUE:{}'.format(school)
    _get_seiue_client.cache_clear()
    db_cache.set(key, info, timeout=None)


def get_attendance_rule(school):
    key = 'ATTENDANCE_RULE:{}'.format(school)
    value = db_cache.get(key)
    if not value:
        value = {"later_time": 10}
        old_key = 'ATTENDANCE_RULE'
        value = db_cache.get(old_key, default=value)
        db_cache.delete(old_key)
        db_cache.set(key, value, timeout=None)
    return value


def set_attendance_rule(school, rule):
    key = 'ATTENDANCE_RULE:{}'.format(school)
    db_cache.set(key, rule, timeout=None)


def get_virth_users():
    key = 'NIRVANA_VIRTH_USER'
    default = {
        cst.DEFAULT_CLIENT_ID: cst.DEFAULT_CLIENT_SECRET
    }
    value = db_cache.get_or_set(key, default, timeout=None)
    return value


def add_virth_user(client_id, client_secret):
    key = 'NIRVANA_VIRTH_USER'
    value = db_cache.get(key, {})
    value[client_id] = client_secret
    db_cache.set(key, value, timeout=None)


def del_virth_user(client_id):
    key = 'NIRVANA_VIRTH_USER'
    value = db_cache.get(key, {})
    value.pop(client_id, None)
    if value:
        db_cache.set(key, value, timeout=None)
    else:
        db_cache.delete(key)


def set_permission_info(project_label, data):
    key = 'NIRVANA_PERMISSION_INFO:{}'.format(project_label)
    db_cache.set(key, data, timeout=None)


def del_permission_info(project_label):
    key = 'NIRVANA_PERMISSION_INFO:{}'.format(project_label)
    db_cache.delete(key)


def get_permission_info(project_label):
    key = 'NIRVANA_PERMISSION_INFO:{}'.format(project_label)
    data = db_cache.get(key)
    return data


def get_project_labels():
    key = 'NIRVANA_PROJECT_LABELS'
    project_labels = db_cache.get(key, [])
    return project_labels


def add_project_label(project_label):
    key = 'NIRVANA_PROJECT_LABELS'
    project_labels = db_cache.get(key, [])
    if project_label not in project_labels:
        project_labels.append(project_label)
        db_cache.set(key, project_labels, timeout=None)


def del_project_label(project_label):
    key = 'NIRVANA_PROJECT_LABELS'
    project_labels = db_cache.get(key, [])
    if project_label in project_labels:
        project_labels.remove(project_label)
        db_cache.set(key, project_labels, timeout=None)


def get_all_permission_groups():
    project_labels = get_project_labels()
    result = {}
    for project in project_labels:
        result[project] = get_permission_groups(project)
    return result


def get_permission_groups(project_label):
    key = 'NIRVANA_PROJECT_LABEL_PERMISSION_GROUP:{}'.format(project_label)
    value = db_cache.get(key, [])
    return value


def set_permission_groups(project_label, value):
    key = 'NIRVANA_PROJECT_LABEL_PERMISSION_GROUP:{}'.format(project_label)
    db_cache.set(key, value, timeout=None)


def del_permission_groups(project_label):
    key = 'NIRVANA_PROJECT_LABEL_PERMISSION_GROUP:{}'.format(project_label)
    db_cache.delete(key)


def clear_permission_groups():
    project_labels = get_project_labels()
    for project in project_labels:
        key = 'NIRVANA_PROJECT_LABEL_PERMISSION_GROUP:{}'.format(project)
        db_cache.delete(key)


def get_school_course_walking_flag(school, manager):
    key = 'NIRVANA_WALKING_COURSE:{}_{}'.format(school, manager)
    value = db_cache.get(key, False)
    return value


def set_school_course_walking_flag(school, manager, value):
    key = 'NIRVANA_WALKING_COURSE:{}_{}'.format(school, manager)
    db_cache.set(key, value, timeout=None)
