from django.contrib import admin
from livestock.models import *


class LiveStockModelAdmin(admin.ModelAdmin):
    list_display = ["live_stock_id", "breed", "is_pregnant", "last_calvation_date", "purchase_price", "milk_capacity_display", "parity", "created_at"]

    @admin.display(empty_value="NA")
    def milk_capacity_display(self, obj):
        return str(obj.milk_capacity) + ' L'


class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'is_active']


class AnimalModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'is_active']


admin.site.register(LiveStockModel, LiveStockModelAdmin)
admin.site.register(ProductsModel, ProductModelAdmin)
admin.site.register(AnimalModel, AnimalModelAdmin)
