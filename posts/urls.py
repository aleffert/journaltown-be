"""posts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.http import HttpResponse
from django.urls import path, include
from rest_framework import routers
from posts.views import posts, users, registration


router = routers.DefaultRouter()
router.register(r'users', users.UserViewSet)
router.register(r'posts', posts.PostViewSet)

urlpatterns = [
    path('', lambda request: HttpResponse('{}')),
    path('health', lambda request: HttpResponse('{}')),
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('', include('drfpasswordless.urls')),
    path('me/', users.CurrentUserView.as_view()),
    path('register/email/', registration.send_token_email),
    path('callback/register/', registration.register_email_callback),
    path('users/<username>/available/', registration.is_available)
]
