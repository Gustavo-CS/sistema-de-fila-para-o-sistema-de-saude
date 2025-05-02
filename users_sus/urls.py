from django.urls import path, include
from . import views
from django.contrib import admin

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login_view"),
    path("logout/", views.logout_view, name="logout"),
    path("create/", views.create_view, name="create"),
    
    path('auth-receiver', views.auth_receiver, name='auth_receiver'),
]