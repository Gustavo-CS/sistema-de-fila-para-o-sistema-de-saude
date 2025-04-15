from django.db import models
from django.contrib.auth.models import AbstractBaseUser


# Create your models here.
class User(AbstractBaseUser):
    # TODO: Completar com os campos apropriados <--------------------------------------------------------------
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    birth_date = models.DateField()
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'


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