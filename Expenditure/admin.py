from django.contrib import admin
from Expenditure.models import *
from django.urls import path
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect


class ExpenditureAdmin(admin.ModelAdmin):
    list_display = ["id", "amount", "category"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path("politician-data/import-excel/", self.admin_site.admin_view(UploadPoliticianData.as_view()), name="import_politician_data"),
                ]
        return my_urls + urls


class UploadPoliticianData(TemplateView):
    template_name = "admin/Expenditure/override_excel.html"
    def get(self, request):
        return render(request, self.template_name)
    def post(self, request):
        return HttpResponseRedirect('/admin/Expenditure/expendituremodel/')

admin.site.register(ExpenditureModel, ExpenditureAdmin)
