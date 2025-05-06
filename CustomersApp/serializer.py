from rest_framework import serializers
from CustomersApp.models import CustomerSubscriptionModel


class CustomersListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerSubscriptionModel
        fields = ['id', 'subscription', 'price_at_subscription', 'start_date', 'end_date', 'delivery_schedule', 'delivery_agent']
