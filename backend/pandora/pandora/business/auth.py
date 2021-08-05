# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import re

regex_edge = re.compile(r"Edge/[0-9.]*$")
regex_chrome = re.compile(r"Chrome/[0-9.]*$")
regex_safari = re.compile(r"Safari/[0-9.]*$")
regex_opera = re.compile(r"OPR/[0-9.].*$")
regex_safari = re.compile(r"Firefox/[0-9.]*$")

regex_browser_list = [
    regex_edge, regex_chrome, regex_safari, regex_opera, regex_safari
]
browser_map = {
    "OPR": "Opera"
}

re_android = re.compile(r"Android [0-9.]*")
msie = re.compile(r"MSIE [0-9.]*")


def get_user_agent_info(request):
    user_agent = request.META.get("HTTP_USER_AGENT")
    browser = "Other Browsers"
    for regex_browser in regex_browser_list:
        browser_search = re.search(regex_browser, user_agent)
        if browser_search:
            browser = browser_search.group()
            continue
    return {
        "browser": browser,
        "platform": "",
        "os": ""
    }


def get_remote_ip(request):
    if "HTTP_X_FORWARDED_FOR" in request.META.keys():
        ip = request.META["HTTP_X_FORWARDED_FOR"]
    else:
        ip = request.META["REMOTE_ADDR"]
    return ip
