from rest_framework import serializers
from CustomersApp.models import *
from authentication.serializer import UserDetailsSerializer
from datetime import datetime
from django.db.models import Sum


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


class CustomerBaseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerSubscriptionModel
        ['id', 'user', 'subscription', 'start_date', 'delivery_agent', 'schedule']


class CustomerBaseSerializer(serializers.ModelSerializer):
    schedule = serializers.SerializerMethodField()
    delivery_agent = UserDetailsSerializer()
    subscription = serializers.SerializerMethodField()
    user = UserDetailsSerializer()
    pending_payments = serializers.SerializerMethodField()
    total_turnover = serializers.SerializerMethodField()
    payments_pending_count = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()

    class Meta:
        model = CustomerSubscriptionModel
        fields = ['id', 'user', 'subscription', 'start_date', 'delivery_agent', 'schedule', 'pending_payments', 'total_turnover', 'payments_pending_count']

    def get_subscription(self, obj):
        try:
            return str(obj.subscription)
        except:
            pass

    def get_schedule(self, obj):
        return obj.subscription.get_schedule_display()

    def get_pending_payments(self, obj):
        data = []

        for item in obj.pending_payments:
            temp = {}
            temp['year'] = item.month.year
            temp['month'] = datetime.strftime(item.month, '%B')
            temp['amount_due'] = item.amount_due
            data.append(temp)

        return data

    def get_total_turnover(self, obj):
        return obj.total_turnover

    def get_payments_pending_count(self, obj):
        return obj.payments_pending_count
    
    def get_start_date(self, obj):
        if obj.start_date:
            return datetime.strftime(obj.start_date, '%d %B %Y')


class CustomersListSerializer(CustomerBaseSerializer):
    pass


class CustomersWriteSerializer(CustomerBaseWriteSerializer):
    pass


class CustomersListSerializerForWeb(CustomerBaseSerializer):
    class Meta:
        model = CustomerSubscriptionModel
        fields = ['user', 'subscription', 'start_date', 'delivery_agent', 'schedule', 'total_turnover', 'payments_pending_count']


class CustomerDetailsByIdSerializer(CustomerBaseSerializer):
    class Meta:
        model = CustomerSubscriptionModel
        fields = ['user', 'subscription', 'start_date', 'delivery_agent', 'schedule', 'pending_payments', 'total_turnover']

############### Payments ###################


class PaymentsListingSerializer(serializers.ModelSerializer):
    amount_due = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)

    customer = serializers.SerializerMethodField()
    class Meta:
        model = MonthlyPaymentModel
        fields = ['customer', 'amount_due', 'amount_paid', 'is_paid', 'id']

    def get_customer(self, obj):
        return {'id': obj.customer.user_id, 'name': obj.customer.user.name}
