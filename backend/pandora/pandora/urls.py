"""pandora URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from rest_framework_swagger.views import get_swagger_view
from django.conf import settings
from django.conf.urls.static import static

PANDORA_VERSION = "v1"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/PANDORA_VERSION/', include('pandora.api.endpoints.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.FILE_URL, document_root=settings.FILE_ROOT)
    urlpatterns += static(settings.UPGRADE_URL, document_root=settings.UPGRADE_ROOT)

urlpatterns += [
    path('docs2/', include_docs_urls(title='pandora', authentication_classes=[],
                                     permission_classes=[])),
    path('docs/', get_swagger_view(title='pandora')),
]
if settings.SILK:
    urlpatterns += [
        path('silk/', include('silk.urls', namespace='silk')),
    ]
