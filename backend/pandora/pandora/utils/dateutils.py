import datetime
from django.utils import timezone
import random


# 传入datetime,如果punchtime在(starttime, endtime)范围内返回TRUE
# 格式要求：punchtime:datetime.datetime, starttime,endtime:datetime.time
def is_in(punchtime, starttime, endtime):
    punchtime_int = int(datetime.datetime.strftime(punchtime, "%H%M%S"))
    starttime_int = int(datetime.time.strftime(starttime, "%H%M%S"))
    endtime_int = int(datetime.time.strftime(endtime, "%H%M%S"))
    if (punchtime_int >= starttime_int) and (punchtime_int <= endtime_int):
        return True
    else:
        return False


# 传入string,如果punchtime在(starttime, endtime)范围内返回TRUE
# 格式要求：punchtime:'2018-05-07 11:00:00', starttime,endtime:'11:00:00'
def is_in_str(punchtime, starttime, endtime):
    punchtime_int = int(
        datetime.datetime.strftime(datetime.datetime.strptime(punchtime, "%Y-%m-%d %H:%M:%S"), "%H%M%S"))
    starttime_int = int(datetime.datetime.strftime(datetime.datetime.strptime(starttime, "%H:%M:%S"), "%H%M%S"))
    endtime_int = int(datetime.datetime.strftime(datetime.datetime.strptime(endtime, "%H:%M:%S"), "%H%M%S"))
    if (punchtime_int >= starttime_int) and (punchtime_int <= endtime_int):
        return True
    else:
        return False


# 传入string如("2018-05-07"，"2018-05-09")
# 返回[{'date': '2018-05-07', 'weekday': 1}, {'date': '2018-05-08', 'weekday': 2}, {'date': '2018-05-09', 'weekday': 3}]
# 星期一~星期日对应（1~7）
def date_list(begin, end):
    if not begin:
        begin_day = timezone.now()
    else:
        begin_day = datetime.datetime.strptime(begin, '%Y-%m-%d')

    if not end:
        end_day = timezone.now()
    else:
        end_day = datetime.datetime.strptime(end, '%Y-%m-%d')

    datelist = []
    for i in range((end_day - begin_day).days + 1):
        day = begin_day + datetime.timedelta(days=i)
        date = {
            'date': day.strftime('%Y-%m-%d'),
            'datetime': day,
            'weekday': day.isoweekday()
        }
        datelist.append(date)
    return datelist


def range_date(begin, end):
    date_list = []
    for i in range((end - begin).days + 1):
        day = begin + datetime.timedelta(days=i)
        date_list.append(day)
    return date_list


def rand_time(begin, end):
    return datetime.datetime.fromtimestamp(random.uniform(begin.timestamp(), end.timestamp()))


def str2_date(date_str):
    if not date_str:
        return None
    try:
        return timezone.datetime.strptime(date_str, '%Y-%m-%d')
    except (Exception,):
        pass
    raise AttributeError('wrong time format')


def str2_time(time_str):
    if not time_str:
        return None
    format_list = ["%H:%M:%S.%f", "%H:%M:%S"]
    for _format in format_list:
        try:
            date_time = timezone.datetime.strptime(time_str, _format).time()
            return date_time
        except (Exception,):
            pass
    raise AttributeError('wrong time format')


def str2datetime(time_str, format_list=None):
    if not time_str:
        return None
    if isinstance(time_str, timezone.datetime):
        return time_str

    if not format_list or not isinstance(format_list, list):
        format_list = ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S",
                       "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S.%fZ"]

    for _ in format_list:
        try:
            date_time = timezone.datetime.strptime(time_str, _)
            return date_time
        except (Exception,):
            pass
    raise AttributeError('wrong time format')


def datetime2str_z(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ") if dt else None


def datetime2str(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None


def date2str(dt):
    return dt.strftime("%Y-%m-%d") if dt else None


def str2time_period(time_str, minutes=30):
    """
    :param time_str:  11:00-12:00
    :return: (pre, begin, end, post): (10:30, 11:00,12:00, 12:30)
    """

    try:
        begin, end = time_str.split("-")
        begin = timezone.datetime.strptime(begin, '%H:%M')
        end = timezone.datetime.strptime(end, '%H:%M')
        pre = begin - timezone.timedelta(minutes=minutes)
        post = end + timezone.timedelta(minutes=minutes)
        return pre.time(), begin.time(), end.time(), post.time()
    except (Exception,):
        raise AttributeError('wrong time format, need 11:00-12:00')


def str2time_period_extra(time_str, pre_minutes=30, pre_start_minutes=0, pre_end_minutes=5):
    """
    :param time_str:  11:00-12:00
    :param pre_minutes:  30
    :param pre_start_minutes:  0
    :param pre_end_minutes:  5
    :return: (pre, begin, end, pre_start, pre_end): (11:00, 12:00, 10:30, 11:00, 11:05, )
    """

    try:
        begin, end = time_str.split("-")
        begin = timezone.datetime.strptime(begin, '%H:%M')
        end = timezone.datetime.strptime(end, '%H:%M')
        pre = begin - timezone.timedelta(minutes=pre_minutes)
        pre_start = begin + timezone.timedelta(minutes=pre_start_minutes)
        pre_end = begin + timezone.timedelta(minutes=pre_end_minutes)
        return begin.time(), end.time(), pre.time(), pre_start.time(), pre_end.time()
    except (Exception,):
        raise AttributeError('wrong time format, need 11:00-12:00')


def get_latest_days(days=7):
    today = datetime.date.today()
    weeks = []
    for _ in range(days):
        weeks.append(today.strftime('%Y%m%d'))
        today -= datetime.timedelta(days=1)
    return weeks


def format_datetime(date, time):
    return timezone.datetime.combine(date, time)
    # return timezone.datetime.strptime("{} {}".format(date.strftime("%Y-%m-%d"), time.strftime("%H:%M:%S")),
    #                                   "%Y-%m-%d %H:%M:%S")
