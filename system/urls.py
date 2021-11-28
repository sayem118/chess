"""system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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

from clubs import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('', views.home, name='home'),
    path('start/', views.start, name='start'),
    path('password/', views.password, name='password'),
    path('log_out/', views.log_out, name='log_out'),
    path('user_list/', views.user_list, name='user_list'),
    path('member_status/', views.member_status, name='member_status'),
    path('profile/', views.profile, name='profile'),
    path('approve_applicant/<int:user_id>', views.approve_applicant, name='approve_applicant')
]
