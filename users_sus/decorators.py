from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def worker_required(function=None, redirect_field_name=None, login_url='login_worker'):
    """
    Decorator for views that checks that the user is logged in AND is a Worker.
    Redirects to login_worker if not authenticated or not a worker.
    """
    def check_is_worker(user):
        # Verifica se o usuário está autenticado e se tem um objeto Worker associado.
        return user.is_authenticated and hasattr(user, 'worker') and user.worker.is_active

    actual_decorator = user_passes_test(
        check_is_worker,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
