from rest_framework import serializers
from CustomersApp.models import *
from authentication.serializer import UserDetailsSerializer


class SubscriptionDetailsSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    animal = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionPlanModel
        fields = ['id', 'animal', 'product', 'price', 'quantity']

    def get_product(self, obj):
        try:
            return obj.product.name
        except:
            return ""
    def get_animal(self, obj):
        try:
            return obj.animal.name
        except:
            return ""


class CustomerBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerSubscriptionModel
        fields = ['id', 'user', 'subscription', 'start_date', 'delivery_schedule', 'delivery_agent']


class CustomersListSerializer(CustomerBaseSerializer):
    delivery_agent = UserDetailsSerializer()
    subscription = SubscriptionDetailsSerializer()
    user = UserDetailsSerializer()


class CustomersWriteSerializer(CustomerBaseSerializer):
    pass
