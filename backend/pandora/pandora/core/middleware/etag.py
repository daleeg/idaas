# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import hashlib

from django.conf import settings
from django.http import HttpResponse
from django.utils.http import quote_etag
from django.utils.deprecation import MiddlewareMixin
from django.utils.cache import cc_delim_re, get_conditional_response, set_response_etag

from pandora.core.cachedependency import client
from pandora.utils.fileutils import get_url_path_md5

LOG = logging.getLogger(__name__)


class ConditionalEtagCacheMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == "GET":
            path = request.path
            etag = None
            response = None
            if path.startswith(settings.STATIC_URL) or path.startswith(settings.FILE_URL) or path.startswith(
                    settings.UPGRADE_URL):
                md5 = get_url_path_md5(path)
                if md5:
                    etag = quote_etag(md5)
            else:
                if settings.API_CACHE_ON:
                    company_id = request.company_id
                    tables = client.mapping.get_api_company_dependent_tables(company_id, path)
                    if client.can_cache(company_id, request.user, path, request.method) and tables:
                        LOG.info("can cache")
                        values = client.get_tables_last_modify(tables)
                        LOG.debug("dependents: {}".format(values))
                        ticket = client.gen_ticket(values)
                        etag = quote_etag(ticket)
                        full_path = request.get_full_path()
                        ret, response = client.get_api_cache_data(company_id, full_path, ticket)
                        if not ret:
                            LOG.info("miss cache: {}".format(full_path))
                            setattr(request, "missing_cache", True)
                        else:
                            LOG.info("hit cache: {}".format(full_path))

            setattr(request, "etag", etag)
            if etag:
                response = get_conditional_response(
                    request,
                    etag=etag,
                    response=response,
                )
                if response:
                    return response

    def process_response(self, request, response):
        # It"s too late to prevent an unsafe request with a 412 response, and
        # for a HEAD request, the response body is always empty so computing
        # an accurate ETag isn"t possible.
        if request.method != "GET":
            return response
        if not isinstance(response, HttpResponse):
            return response

        if response and (200 <= response.status_code < 300):
            response_data = getattr(response, "data", None)
            if response_data and response_data.get("code", 1) != 0:
                return response
            etag = getattr(request, "etag", None)
            missing_cache = getattr(request, "missing_cache", False)
            if missing_cache:
                company_id = request.company_id
                path = request.path
                tables = client.mapping.get_api_dependent_tables(company_id, path)
                if tables:
                    values = client.get_tables_last_modify(tables)
                    LOG.debug("dependents: {}".format(values))
                    ticket = client.gen_ticket(values)
                    full_path = request.get_full_path()
                    if "json" in response["Content-Type"]:
                        client.set_api_cache_data(company_id, full_path, ticket,
                                                  response.data["data"],
                                                  response.headers)
                    etag = quote_etag(ticket)
            if self.needs_cache(response) and not response.has_header("ETag"):
                if etag:
                    response["ETag"] = etag
                elif not response.streaming:
                    etag = quote_etag(hashlib.md5(response.content).hexdigest())
                    response["ETag"] = quote_etag(hashlib.md5(response.content).hexdigest())
                    response = get_conditional_response(
                        request,
                        etag=etag,
                        response=response,
                    )
        return response

    def needs_cache(self, response):
        """Return True if an ETag header should be added to response."""
        cache_control_headers = cc_delim_re.split(response.get("Cache-Control", ""))
        return all(header.lower() != "no-store" for header in cache_control_headers)
