# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.urls import path
from django.urls import include

from pandora.core.routers import APIRouter

router = APIRouter()


urlpatterns = [
    path("", include(router.urls)),

]
