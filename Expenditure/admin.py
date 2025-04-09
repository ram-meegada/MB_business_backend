from django.contrib import admin
from Expenditure.models import *
from django.urls import path
from django.shortcuts import render


class ExpenditureAdmin(admin.ModelAdmin):
    list_display = ["id", "amount", "category", "created_at"]


class ExpenditureCategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "parent", "created_at"]
    search_fields = ["name"]

admin.site.register(ExpenditureModel, ExpenditureAdmin)
admin.site.register(ExpenditureCategoryModel, ExpenditureCategoryAdmin)
