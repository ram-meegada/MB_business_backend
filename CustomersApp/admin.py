from django.contrib import admin
from datetime import datetime
from CustomersApp.models import *


class SubscriptionPlanModelAdmin(admin.ModelAdmin):
    list_display = ['product', 'animal', 'description', 'schedule', 'quantity', 'price', 'evening_quantity', 'evening_price']


class CustomerSubscriptionModelAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'subscription_description', 'start_date']
    search_fields = ['user__name']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "delivery_agent":
            kwargs["queryset"] = UserModel.objects.filter(role=3)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    @admin.display()
    def customer_name(self, obj):
        return obj.user.name

    @admin.display()
    def subscription_description(self, obj):
        return obj.subscription.description


@admin.action(description="Mark order status as delivered")
def mark_order_status_delivered(modeladmin, request, queryset):
    queryset.update(status="delivered")
    modeladmin.message_user(request, f"Selected orders status is changed to delivered")

class OrdersModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'subscribed_customer', 'schedule_date', 'status', 'is_morning_delivery']
    search_fields = ['customer__user__name']
    raw_id_fields = ['customer']
    actions = [mark_order_status_delivered]

    @admin.display()
    def subscribed_customer(self, obj):
        return obj.customer.user.name


class MonthlyPaymentModelAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'payments_month', 'amount_due', 'amount_paid']
    search_fields = ['customer__user__name']

    @admin.display(empty_value="NA")
    def customer_name(self, obj):
        return obj.customer.user.name if obj.customer else None
    
    @admin.display(empty_value="NA")
    def payments_month(self, obj):
        return datetime.strftime(obj.month, "%B %Y")


admin.site.register(SubscriptionPlanModel, SubscriptionPlanModelAdmin)
admin.site.register(CustomerSubscriptionModel, CustomerSubscriptionModelAdmin)
admin.site.register(OrdersModel, OrdersModelAdmin)
admin.site.register(MonthlyPaymentModel, MonthlyPaymentModelAdmin)
