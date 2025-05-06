from django.contrib import admin
from authentication.models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'role', 'phone_num', 'is_superuser']


admin.site.register(UserModel, UserAdmin)
