"""jerry_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path,include
from django.conf import settings

from django.conf.urls.static import static
from render.urls import urlpatterns as render_urlpatterns
from jerry_project.router import routers
from user.views import VerifyEmailViewset,ResetPasswordViewSet,ResendOtpViewSet
from render.views import custom_404_view
from user.admin import creator_admin_site, admin_admin_site


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('api/',include(routers.urls)),
    path('api/verify-otp/<str:token>/',VerifyEmailViewset.as_view({"post":"create"})),
    path('api/reset-password/<str:token>/',ResetPasswordViewSet.as_view({"post":"create"})),
    path('api/resend-otp/<str:token>/',ResendOtpViewSet.as_view({"post":"create"})),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('admin/', creator_admin_site.urls),
    path('admin/database-management/', admin_admin_site.urls), 
    path('',include(render_urlpatterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'render.views.custom_404_view'