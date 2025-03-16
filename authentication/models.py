from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class UserModel(AbstractBaseUser):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    name = models.CharField(max_length=100)
    password = models.TextField()

    class Meta:
        db_table = 'Users'
