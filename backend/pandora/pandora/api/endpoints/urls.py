# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.urls import path
from django.urls import include
from pandora.api import endpoints as eps
from pandora.core.routers import APIRouter
from pandora.core.endpoints.viewjoin import join_path

router = APIRouter()
urlpatterns = [
    path("", include(router.urls)),
    path("", include("pandora.api.endpoints.base.urls")),
    path("", include("pandora.api.endpoints.account.urls")),

    path("", include("pandora.api.endpoints.auth.urls")),
    path("audit/", include("pandora.api.endpoints.audit.urls")),
    path("version/", eps.VersionEndpoint.as_view()),

]
