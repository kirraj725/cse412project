"""
URL configuration for cse412proj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from rewards import views as rewards_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', rewards_views.index, name='home'),

    #api endpoints
    path('api/login/', rewards_views.api_login, name='api_login'),
    path("api/register/", rewards_views.api_register, name="api_register"),
    path('api/account/', rewards_views.api_account, name='api_account'),
    path('api/rewards/', rewards_views.api_rewards, name='api_rewards'),
    path('api/stores/', rewards_views.api_stores, name='api_stores'),
    path("api/vendors/", rewards_views.api_vendors, name='api_vendors'),
    path("api/exchange/", rewards_views.api_exchange, name="api_exchange"),
    path("api/logout/", rewards_views.api_logout, name="api_logout"),
]
