"""pandora URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path("", views.home, name="home")
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path("", Home.as_view(), name="home")
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path("blog/", include("blog.urls"))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.documentation import include_docs_urls
from rest_framework_swagger.views import get_swagger_view
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
import re
from django.views.static import serve
from rest_framework.schemas import get_schema_view as rs
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from pandora.core.static import static_serve
import os

schema_view = get_schema_view(
    info=openapi.Info(
        title="IDAAS API",
        default_version="v1",
        description="IDAAS API doc",
        terms_of_service="",
        contact=openapi.Contact(name="JDSK Group", email="service@jd.com"),
        license=openapi.License(name="BSD License"),

    ),
    url="http://www.baidu.com",
    public=True,
    permission_classes=(permissions.AllowAny,),
)

api_version = os.path.join(settings.PANDORA_API, "<str:version>/").lstrip("/")

urlpatterns = [
    path(os.path.join(api_version, "admin/").lstrip("/"), admin.site.urls),
    path(api_version, include("pandora.api.endpoints.urls")),

]
if settings.DEBUG:
    urlpatterns += [
        re_path(r"^%s(?P<path>.*)$" % re.escape(settings.STATIC_URL.lstrip("/")), static_serve, name="static"),
        re_path(r"^%s(?P<path>.*)$" % re.escape(settings.FILE_URL.lstrip("/")), serve, name="file"),
        re_path(r"^%s(?P<path>.*)$" % re.escape(settings.UPGRADE_URL.lstrip("/")), serve, name="upgrade"),
        path(os.path.join(api_version, "docs/"), schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
        path(os.path.join(api_version, "redoc/"), schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    ]
    if settings.SILK:
        urlpatterns += [
            path(os.path.join(api_version, "silk/"), include("silk.urls", namespace="silk")),
        ]
