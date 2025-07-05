from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from utils.commonUtils import BaseModel


class UserModel(AbstractBaseUser, PermissionsMixin, BaseModel):
    ROLE_CHOICES = [
        (1, "Admin"),
        (2, "Customer"),
        (3, "Delivery agent")
    ]

    username = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='images', blank=True, null=True)
    phone_num = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    name = models.CharField(max_length=100)
    is_staff = models.BooleanField(default=False)
    role = models.IntegerField(choices=ROLE_CHOICES, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
