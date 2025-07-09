"""
URL configuration for healify project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
import healytics
from django.urls import include, path
from healytics import views
import healytics.urls
import accounts.urls
from django.contrib import admin
import healytics
from django.urls import include, path
from healytics import views
import healytics.urls
import accounts.urls
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.index),
    path("admin/", admin.site.urls),
    path("home/", views.index),
    path("healytics/", include(healytics.urls)),
    path('admin/', admin.site.urls),  # Inclus les URLs de ton app
    path('accounts/', include('accounts.urls')),
    path('assistant/', include('assistant_medical.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)