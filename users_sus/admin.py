from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from django.utils.translation import gettext_lazy as _ 

from .models import HealthUnit, User, Patient, Worker, Code

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_staff', 'is_active', 'is_superuser')

    list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups')

    search_fields = ('email', 'username')

    readonly_fields = ('date_joined', 'last_login') 
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('username', 'birth_date')}), 
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    # Campos para o formulário de adição de novo usuário
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'birth_date', 'password'),
        }),
    )
    # Garante que o campo 'password' será um campo de senha e não texto simples
    ordering = ('email',)

# Register your models here.
admin.site.register(Worker)
admin.site.register(Code)
admin.site.register(Patient)
admin.site.register(User, CustomUserAdmin) 
admin.site.register(HealthUnit)
