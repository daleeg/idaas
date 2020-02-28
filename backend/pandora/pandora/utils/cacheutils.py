# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.cache import cache
from nirvana.utils.keyvalue_utils import get_site_info, set_site_info
from nirvana.utils.weatherutils import get_weacher_adcode, get_weather_from_api
import logging

LOG = logging.getLogger(__name__)


def get_login_count(school, user):
    key = 'LOGIN-{}:{}'.format(school, user)
    value = cache.get(key)
    return 0 if value is None else value


def incr_and_get_login_count(school, user):
    key = 'LOGIN-{}:{}'.format(school, user)
    value = cache.get(key)
    new_value = 1 if value is None else value + 1
    cache.set(key, new_value, 60)
    return new_value


def clear_login_count(school, user):
    key = 'LOGIN-{}:{}'.format(school, user)
    if key in cache:
        cache.delete(key)


def set_sn_token(school, sn, value, timeout=3600):
    key = 'SN_TOKEN-{}:{}'.format(school, sn)
    cache.set(key, value, timeout)


def get_sn_token(school, sn):
    key = 'SN_TOKEN-{}:{}'.format(school, sn)
    value = cache.get(key)
    return value


def get_expire_token(key):
    token_key = 'TOKEN:{}'.format(key)
    value = cache.get(token_key)
    return value


def set_expire_token(key, value, timeout=1200):
    token_key = 'TOKEN:{}'.format(key)
    cache.set(token_key, value, timeout)


def delete_expire_token(key):
    token_key = 'TOKEN:{}'.format(key)
    cache.delete(token_key)


def get_school_info(key):
    school_key = 'X-SCHOOL:{}'.format(key)
    value = cache.get(school_key)
    return value


def set_school_info(key, value, timeout=1200):
    school_key = 'X-SCHOOL:{}'.format(key)
    cache.set(school_key, value, timeout)


def delete_school_info(key):
    school_key = 'X-SCHOOL:{}'.format(key)
    cache.delete(school_key)


def get_current_school():
    key = 'NIRVANA_CURRENT_SCHOOL'
    value = cache.get(key)
    return value


def set_current_school(school):
    key = 'NIRVANA_CURRENT_SCHOOL'
    cache.set(key, school, timeout=None)


def clear_current_school():
    key = 'NIRVANA_CURRENT_SCHOOL'
    cache.delete(key)


def get_project_labels(school):
    key = 'NIRVANA_PROJECT_LABELS:{}'.format(school)
    value = cache.get(key)
    return value


def set_project_labels(school, values):
    key = 'NIRVANA_PROJECT_LABELS:{}'.format(school)
    cache.set(key, values, timeout=None)


def clear_project_labels(school):
    key = 'NIRVANA_PROJECT_LABELS:{}'.format(school)
    cache.delete(key)


def get_weather_info(school):
    key = 'WEATHER_INFO:{}'.format(school)
    value = cache.get(key)
    if value is None:
        value = _set_weather_from_api(school)
    return value


def delete_weather_info(school):
    key = 'WEATHER_INFO:{}'.format(school)
    cache.delete(key)


def _set_weather_from_api(school):
    location_info = get_site_info(school)
    adcode = location_info.get('ADCode')
    province = location_info.get('province')
    city = location_info.get('city')
    if province and city and not adcode:
        adcode = get_weacher_adcode(province, city)
        if adcode:
            new_value = {
                'province': province,
                'city': city,
                'ADCode': adcode
            }
            set_site_info(school, new_value)

    if adcode is None and city is None:
        return 'NoADCode'
    # adcode = adcode if adcode else get_weacher_adcode(province, city)
    value = get_weather_from_api(adcode)
    cache.set('WEATHER_INFO:{}'.format(school), value, 4500)
    return value


def get_license(school):
    key = 'NIRVANA_LICENSE:{}'.format(school)
    value = cache.get(key)
    return value


def set_license(school, value, timeout=3600):
    key = 'NIRVANA_LICENSE:{}'.format(school)
    cache.set(key, value, timeout)


def clear_license(school):
    key = 'NIRVANA_LICENSE:{}'.format(school)
    cache.delete(key)


def set_permissions(group, value, timeout=600):
    key = 'NIRVANA_PERMISSIONS:{}'.format(group)
    cache.set(key, value, timeout)


def get_permissions(group):
    key = 'NIRVANA_PERMISSIONS:{}'.format(group)
    value = cache.get(key, )
    return value if value else []


def clear_permissions(group):
    key = 'NIRVANA_PERMISSIONS:{}'.format(group)
    cache.delete(key, )


def set_permissions_tree(group, value, timeout=600):
    key = 'NIRVANA_PERMISSIONS_TREE:{}'.format(group)
    cache.set(key, value, timeout)


def get_permissions_tree(group):
    key = 'NIRVANA_PERMISSIONS_TREE:{}'.format(group)
    value = cache.get(key, )
    return value if value else []


def clear_permissions_tree(group):
    key = 'NIRVANA_PERMISSIONS_TREE:{}'.format(group)
    cache.delete(key, )


def get_current_semester(school, category):
    key = 'NIRVANA_SEMESTER:{}-{}'.format(school, category)
    value = cache.get(key, )
    return value if value else {}


def set_current_semester(school, category, data, timeout=36000):
    key = 'NIRVANA_SEMESTER:{}-{}'.format(school, category)
    cache.set(key, data, timeout)


def clear_current_semester(school, category):
    key = 'NIRVANA_SEMESTER:{}-{}'.format(school, category)
    value = cache.delete(key, )
    return value if value else {}


def get_rest_schedule_info(school, schedule):
    key = 'NIRVANA_REST_SCHEDULE_INFO:{}-{}'.format(school, schedule)
    value = cache.get(key, )
    return value if value else {}


def set_rest_schedule_info(school, schedule, data, timeout=36000):
    key = 'NIRVANA_REST_SCHEDULE_INFO:{}-{}'.format(school, schedule)
    cache.set(key, data, timeout)


def clear_rest_schedule_info(school, schedule):
    key = 'NIRVANA_REST_SCHEDULE_INFO:{}-{}'.format(school, schedule)
    cache.delete(key, )


def get_rest_table_info(school, rest_id):
    key = 'NIRVANA_REST_INFO:{}-{}'.format(school, rest_id)
    value = cache.get(key, )
    return value if value else {}


def set_rest_table_info(school, rest_id, data, timeout=36000):
    key = 'NIRVANA_REST_INFO:{}-{}'.format(school, rest_id)
    cache.set(key, data, timeout)


def clear_rest_table_info(school, rest_id):
    key = 'NIRVANA_REST_INFO:{}-{}'.format(school, rest_id)
    cache.delete(key, )


def get_course_table_info(school, course_table):
    key = 'NIRVANA_COURSE_TABLE_INFO:{}-{}'.format(school, course_table)
    value = cache.get(key, )
    return value if value else {}


def set_course_table_info(school, course_table, data, timeout=36000):
    key = 'NIRVANA_COURSE_TABLE_INFO:{}-{}'.format(school, course_table)
    cache.set(key, data, timeout)


def clear_course_table_info(school, course_table):
    key = 'NIRVANA_COURSE_TABLE_INFO:{}-{}'.format(school, course_table)
    cache.delete(key, )


def get_manager_info(school, manager):
    key = 'NIRVANA_MANAGER_INFO:{}-{}'.format(school, manager)
    value = cache.get(key, )
    return value if value else {}


def set_manager_info(school, manager, data, timeout=36000):
    key = 'NIRVANA_MANAGER_INFO:{}-{}'.format(school, manager)
    cache.set(key, data, timeout)


def clear_manager_info(school, manager):
    key = 'NIRVANA_MANAGER_INFO:{}-{}'.format(school, manager)
    cache.delete(key, )


def get_current_semester_info_cache(school):
    key = 'NIRVANA_CURRENT_SEMESTER_INFO:{}'.format(school)
    value = cache.get(key, )
    return value


def set_current_semester_info_cache(school, data, timeout=36000):
    key = 'NIRVANA_CURRENT_SEMESTER_INFO:{}'.format(school)
    cache.set(key, data, timeout)


def clear_current_semester_info_cache(school):
    key = 'NIRVANA_CURRENT_SEMESTER_INFO:{}'.format(school)
    cache.delete(key, )


def get_user_classroom_limit(school_id, project_label, user_id):
    key = 'NIRVANA_USER_CLASSROOM_LIMIT:{}_{}_{}'.format(school_id, project_label, user_id)
    value = cache.get(key, )
    return value


def set_user_classroom_limit(school_id, project_label, user_id, data, timeout=36000):
    key = 'NIRVANA_USER_CLASSROOM_LIMIT:{}_{}_{}'.format(school_id, project_label, user_id)
    cache.set(key, data, timeout)


def clear_user_classroom_limit(school_id, project_label="*", user_id="*"):
    key = 'NIRVANA_USER_CLASSROOM_LIMIT:{}_{}_{}'.format(school_id, project_label, user_id)
    cache.delete_pattern(key, )


def get_user_section_limit(school_id, project_label, user_id):
    key = 'NIRVANA_USER_SECTION_LIMIT:{}_{}_{}'.format(school_id, project_label, user_id)
    value = cache.get(key, )
    return value


def set_user_section_limit(school_id, project_label, user_id, data, timeout=36000):
    key = 'NIRVANA_USER_SECTION_LIMIT:{}_{}_{}'.format(school_id, project_label, user_id)
    cache.set(key, data, timeout)


def clear_user_section_limit(school_id, project_label="*", user_id="*"):
    key = 'NIRVANA_USER_SECTION_LIMIT:{}_{}_{}'.format(school_id, project_label, user_id)
    cache.delete_pattern(key, )


def get_user_data_permission(school_id, project_label, user_id):
    key = 'NIRVANA_USER_DATA_PERMISSION:{}_{}_{}'.format(school_id, project_label, user_id)
    value = cache.get(key, )
    return value


def set_user_data_permission(school_id, project_label, user_id, data, timeout=36000):
    key = 'NIRVANA_USER_DATA_PERMISSION:{}_{}_{}'.format(school_id, project_label, user_id)
    cache.set(key, data, timeout)


def clear_user_data_permission(school_id, project_label, user_id):
    key = 'NIRVANA_USER_DATA_PERMISSION:{}_{}_{}'.format(school_id, project_label, user_id)
    cache.delete_pattern(key, )


def get_user_permission_group(school_id, project_label, user_id):
    key = 'NIRVANA_USER_PERMISSION:{}_{}'.format(school_id, project_label, user_id)
    value = cache.get(key, )
    return value


def set_user_permission_group(school_id, project_label, user_id, data, timeout=36000):
    key = 'NIRVANA_USER_PERMISSION:{}_{}_{}'.format(school_id, project_label, user_id)
    cache.set(key, data, timeout)


def clear_user_permission_group(school_id, project_label="*", user_id="*"):
    key = 'NIRVANA_USER_PERMISSION:{}_{}_{}'.format(school_id, project_label, user_id)
    cache.delete_pattern(key, )


def get_student_attendance_id(manager, student_id, date_str, num):
    key = 'NIRVANA_STUDENT_ATTENDANCE:{}_{}_{}_{}'.format(manager, student_id, date_str, num)
    value = cache.get(key, )
    return value


def set_student_attendance_id(manager, student_id, date_str, num, attendance_id, timeout=86400):
    key = 'NIRVANA_STUDENT_ATTENDANCE:{}_{}_{}_{}'.format(manager, student_id, date_str, num)
    cache.set(key, attendance_id, timeout)


def clear_student_attendance_id(manager="*", student_id="*", date_str="*", num="*"):
    key = 'NIRVANA_STUDENT_ATTENDANCE:{}_{}_{}_{}'.format(manager, student_id, date_str, num)
    cache.delete_pattern(key,)


def get_teacher_attendance_id(manager, teacher_id, date_str, num):
    key = 'NIRVANA_TEACHER_ATTENDANCE:{}_{}_{}_{}'.format(manager, teacher_id, date_str, num)
    value = cache.get(key, )
    return value


def set_teacher_attendance_id(manager, teacher_id, date_str, num, attendance_id, timeout=86400):
    key = 'NIRVANA_TEACHER_ATTENDANCE:{}_{}_{}_{}'.format(manager, teacher_id, date_str, num)
    cache.set(key, attendance_id, timeout)


# use only for signals begin
def set_student_school(student_id, school_id, timeout=None):
    key = 'NIRVANA_STUDENT_SCHOOL:{}'.format(student_id)
    cache.set(key, school_id, timeout)


def get_student_school(student_id):
    key = 'NIRVANA_STUDENT_SCHOOL:{}'.format(student_id)
    value = cache.get(key, )
    return value


def set_section_school(section_id, school_id, timeout=None):
    key = 'NIRVANA_SECTION_SCHOOL:{}'.format(section_id)
    cache.set(key, school_id, timeout)


def get_section_school(section_id):
    key = 'NIRVANA_SECTION_SCHOOL:{}'.format(section_id)
    value = cache.get(key, )
    return value


def set_course_school(course_id, school_id, timeout=None):
    key = 'NIRVANA_COURSE_SCHOOL:{}'.format(course_id)
    cache.set(key, school_id, timeout)


def get_course_school(course_id):
    key = 'NIRVANA_COURSE_SCHOOL:{}'.format(course_id)
    value = cache.get(key, )
    return value


def set_vacation_school(vacation_id, school_id, timeout=None):
    key = 'NIRVANA_VACATION_SCHOOL:{}'.format(vacation_id)
    cache.set(key, school_id, timeout)


def get_vacation_school(vacation_id):
    key = 'NIRVANA_VACATION_SCHOOL:{}'.format(vacation_id)
    value = cache.get(key, )
    return value


def set_manager_semester(manager_id, semester_id, timeout=None):
    key = 'NIRVANA_MANAGER_SEMESTER:{}'.format(manager_id)
    cache.set(key, semester_id, timeout)


def get_manager_semester(manager_id):
    key = 'NIRVANA_MANAGER_SEMESTER:{}'.format(manager_id)
    value = cache.get(key, )
    return value


def set_rest_semester(rest_id, semester_id, timeout=None):
    key = 'NIRVANA_REST_SEMESTER:{}'.format(rest_id)
    cache.set(key, semester_id, timeout)


def get_rest_semester(rest_id):
    key = 'NIRVANA_REST_SEMESTER:{}'.format(rest_id)
    value = cache.get(key, )
    return value

# use only for signals end
