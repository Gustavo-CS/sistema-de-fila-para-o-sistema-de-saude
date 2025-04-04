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