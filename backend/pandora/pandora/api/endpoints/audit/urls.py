# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.urls import path
from django.urls import include

from pandora.api import endpoints as eps
from pandora.core.routers import APIRouter

router = APIRouter()
router.register("token", eps.AuditTokenListViewSet)
router.register("token", eps.AuditTokenRevokeViewSet)

urlpatterns = [
    path('', include(router.urls)),

]
