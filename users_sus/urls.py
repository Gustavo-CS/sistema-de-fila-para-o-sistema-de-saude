from django.urls import path, include
from users_sus import views
from django.contrib import admin

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login_view"),
    path("login_worker/", views.login_worker, name="login_worker"),
    path("logout/", views.logout_view, name="logout"),
    path("create/", views.create_view, name="create"),
    path("manager/", include("users_sus.manager_urls")),
    path('feedback/', views.feedback, name='feedback'),
    path('unidades_por_estado/', views.unidades_por_estado_view, name='unidades_por_estado'),
    path('auth-receiver', views.auth_receiver, name='auth_receiver'),
    path("scheduling/", views.scheduling_view, name="scheduling"),
    path("salvar-agendamento/", views.salvar_agendamento, name="salvar_agendamento"),
    path("meus-agendamentos/", views.meus_agendamentos_view, name="meus_agendamentos"),
    path("sched_logs/", views.sched_logs_view, name="sched_logs"),
    path("queue_display/", views.queue_display_view, name="queue_display"),


    path('fila/<str:numero_senha>/', views.fila_view, name='tela_fila'),
    path('api/status/<str:numero_senha>/', views.api_status_fila, name='api_status_fila'),
    path('search-senhas/', views.search_senhas, name='search_senhas'),
]