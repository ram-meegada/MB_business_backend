from django.contrib import admin
from Expenditure.models import *
from django.urls import path
from django.shortcuts import render


class ExpenditureAdmin(admin.ModelAdmin):
    list_display = ["id", "amount", "category", "created_at"]


class ParentCategoryFilter(admin.SimpleListFilter):
    title = 'Parent Category'
    parameter_name = 'parent_status'

    def lookups(self, request, model_admin):
        return (
            ('main_cat', 'Top-level categories'),
            ('sub_cat', 'Subcategories'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'main_cat':
            return queryset.filter(parent__isnull=True)
        if self.value() == 'sub_cat':
            return queryset.filter(parent__isnull=False)
        return queryset

class ExpenditureCategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "parent", "short_name", "created_at"]
    search_fields = ["name"]
    list_filter = [ParentCategoryFilter]

admin.site.register(ExpenditureModel, ExpenditureAdmin)
admin.site.register(ExpenditureCategoryModel, ExpenditureCategoryAdmin)
