from django.contrib import admin
from CustomersApp.models import *


class SubscriptionPlanModelAdmin(admin.ModelAdmin):
    list_display = ['product', 'animal', 'description', 'price', 'quantity', 'is_active']


class CustomerSubscriptionModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscription', 'price_at_subscription', 'start_date', 'end_date']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "delivery_agent":
            kwargs["queryset"] = UserModel.objects.filter(role=3)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class OrdersModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'subscription', 'schedule_date', 'status', 'is_morning_delivery']
    raw_id_fields = ['subscription']

admin.site.register(SubscriptionPlanModel, SubscriptionPlanModelAdmin)
admin.site.register(CustomerSubscriptionModel, CustomerSubscriptionModelAdmin)
admin.site.register(OrdersModel, OrdersModelAdmin)
