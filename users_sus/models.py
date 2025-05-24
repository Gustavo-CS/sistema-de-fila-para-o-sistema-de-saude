from django.db import models
from django.contrib.auth.models import AbstractBaseUser
import uuid
from django.utils import timezone

# Create your models here.
class User(AbstractBaseUser):
    # TODO: Completar com os campos apropriados <--------------------------------------------------------------
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    birth_date = models.DateField()
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    patient_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=11, blank=True)



class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True)


class TipoSenha(models.TextChoices):
    NORMAL = 'N', 'Normal'
    PRIORITARIA = 'P', 'Prioritária'


class Code(models.Model):
    id = models.BigAutoField(primary_key=True)
    type_of_code = models.CharField(
        max_length=1,
        choices=TipoSenha.choices,
        default=TipoSenha.NORMAL
    )
    code = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)