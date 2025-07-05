from django.contrib import admin
from authentication.models import *
from django import forms


class UserForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = '__all__'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'role', 'phone_num', 'is_superuser']
    search_fields = ['username', 'name']
    form = UserForm

admin.site.register(UserModel, UserAdmin)
