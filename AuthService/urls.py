"""AuthService URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView, TokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api/api-token-auth/', TokenObtainPairView.as_view()),
    url(r'^api/api-token-refresh/', TokenRefreshView.as_view()),
    url(r'^api/api-token-verify/', TokenVerifyView.as_view()),
    url(r'^api/', include('Users.urls')),
    url(r'^api/', include('Apps.urls')),
]


if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]
    except ImportError:
        pass
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
