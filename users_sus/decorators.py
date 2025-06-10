from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import reverse 

def worker_required(function=None, redirect_field_name=None, login_url='login_worker'): 
    def check_is_worker(user):

        return user.is_authenticated and hasattr(user, 'worker') and user.is_active and user.is_staff

    actual_decorator = user_passes_test(
        check_is_worker,
        login_url=login_url, 
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator