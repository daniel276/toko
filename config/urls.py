"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from main import views as core_views

handler403 = core_views.custom_permission_denied_view
handler404 = core_views.custom_page_not_found_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('main.urls')),
    path('arsip/', include('arsip.urls'), name='arsip'),
    path('403/', core_views.custom_permission_denied_view),
    path('404/', core_views.custom_page_not_found_view),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # THIS MATTER THE MOST TO MAKE UPLOAD HAPPENS!!!