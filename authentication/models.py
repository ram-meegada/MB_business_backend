from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class UserModel(AbstractBaseUser, PermissionsMixin, BaseModel):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    password = models.TextField()
    is_staff = models.BooleanField(default=False)
    is_superuser  = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'Users'
