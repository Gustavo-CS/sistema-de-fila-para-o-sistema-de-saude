from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin 
from django.utils import timezone
from django.conf import settings
from django import forms
from .choices import Estados
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email deve ser fornecido')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    birth_date = models.DateField()
    date_joined = models.DateTimeField(auto_now_add=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="users_sus_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="users_sus_user_permissions",
        related_query_name="user",
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'birth_date']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    patient_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=11, blank=True)

class HealthUnit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    address = models.TextField(blank=True)

class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True)
    health_unit = models.ForeignKey(HealthUnit, on_delete=models.SET_NULL, null=True, blank=True, related_name='workers') 

class StatusSenha(models.TextChoices):
    AGUARDANDO = 'AGU', 'Aguardando'
    CHAMANDO = 'CHA', 'Chamando'
    EM_ATENDIMENTO = 'ATE', 'Em Atendimento'
    ATENDIDO = 'CON', 'Concluído'
    CANCELADO = 'CAN', 'Cancelado'
    PERDEU = 'PER', 'Perdeu a Vez'

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
    status = models.CharField(
        max_length=3,
        choices=StatusSenha.choices,
        default=StatusSenha.AGUARDANDO
    )
    called_at = models.DateTimeField(null=True, blank=True)
    attended_at = models.DateTimeField(null=True, blank=True)
    called_by = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True, related_name='called_codes')
    health_unit = models.ForeignKey(HealthUnit, on_delete=models.CASCADE, related_name='codes') 

    
    class Meta:
        ordering = ['created']

    def __str__(self):
        return f"{self.get_type_of_code_display()} - {self.code}"
    
class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    unidade_sus = models.CharField(max_length=50)
    titulo = models.CharField(max_length=100)
    comentario = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} ({self.unidade_sus})"
    
    # No final do seu models.py

class Agendamento(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agendamentos')
    health_unit = models.ForeignKey(HealthUnit, on_delete=models.CASCADE, related_name='agendamentos')
    especialidade = models.CharField(max_length=100)
    data_agendamento = models.DateTimeField()
    status = models.CharField(max_length=50, default='Confirmado')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario.username} - {self.especialidade} em {self.data_agendamento.strftime("%d/%m/%Y")}'