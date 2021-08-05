from __future__ import unicode_literals


from rest_framework import HTTP_HEADER_ENCODING
from django.conf import settings


def get_company_header(request):
    company = request.META.get("HTTP_{}".format(settings.COMPANY_HEADER), b"")
    if isinstance(company, str):
        company = company.encode(HTTP_HEADER_ENCODING)
    return company


def get_project_label_header(request):
    label = request.META.get("HTTP_{}".format(settings.APP_HEADER), b"")
    if isinstance(label, str):
        label = label.encode(HTTP_HEADER_ENCODING)
    return label
