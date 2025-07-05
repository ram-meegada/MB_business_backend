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
    schedule = serializers.SerializerMethodField()
    delivery_agent = UserDetailsSerializer()
    subscription = serializers.SerializerMethodField()
    user = UserDetailsSerializer()

    class Meta:
        model = CustomerSubscriptionModel
        fields = ['id', 'user', 'subscription', 'start_date', 'delivery_agent', 'schedule']

    def get_subscription(self, obj):
        try:
            return str(obj.subscription)
        except:
            pass
    
    def get_schedule(self, obj):
        return obj.subscription.get_schedule_display()


class CustomersListSerializer(CustomerBaseSerializer):
    pass


class CustomersWriteSerializer(CustomerBaseSerializer):
    pass


class CustomersListSerializerForWeb(CustomerBaseSerializer):
    class Meta:
        model = CustomerSubscriptionModel
        fields = ['user', 'subscription', 'start_date', 'delivery_agent', 'schedule']


############### Payments ###################


class PaymentsListingSerializer(serializers.ModelSerializer):
    amount_due = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)

    customer = serializers.SerializerMethodField()
    class Meta:
        model = MonthlyPaymentModel
        fields = ['customer', 'amount_due', 'amount_paid', 'is_paid']

    def get_customer(self, obj):
        return {'id': obj.customer_id, 'name': obj.customer.user.name}
