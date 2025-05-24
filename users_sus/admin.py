from django.contrib import admin
from .models import Worker, Code, Patient, User
# Register your models here.
admin.site.register(Worker)
admin.site.register(Code)
admin.site.register(Patient)
admin.site.register(User)