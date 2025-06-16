from django.urls import path
from . import manager_views

urlpatterns = [
    path('', manager_views.manager_dashboard, name='manager_dashboard'),
    path('call_next/', manager_views.call_next_code, name='call_next_code'),
    path('update_status/<int:code_id>/', manager_views.update_code_status, name='update_code_status'), 
]