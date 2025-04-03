from django.contrib import admin
from Expenditure.models import *
from django.urls import path
from django.shortcuts import render


class ExpenditureAdmin(admin.ModelAdmin):
    list_display = ["id", "amount", "category"]


admin.site.register(ExpenditureModel, ExpenditureAdmin)
admin.site.register(ExpenditureCategoryModel)
