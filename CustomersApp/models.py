from django.db import models
from utils.commonUtils import BaseModel
from livestock.models import ProductsModel, AnimalModel
from authentication.models import UserModel
from utils.customersUtils import quantity_verbose


class SubscriptionPlanModel(BaseModel):
    QUANTITY_CHOICES = [
        (250, 250),
        (500, 500),
        (750, 750),
        (1000, 1000),
    ]
    product = models.ForeignKey(ProductsModel, on_delete=models.SET_NULL, null=True, verbose_name="Product")
    animal = models.ForeignKey(AnimalModel, on_delete=models.SET_NULL, null=True, verbose_name="Animal")
    description = models.TextField()
    price = models.FloatField()
    quantity = models.IntegerField(choices=QUANTITY_CHOICES)

    def __str__(self):
        return f"{self.animal.name} + {self.product.name} + {quantity_verbose(self.product, self.quantity)} + {self.price}/-"

    class Meta:
        db_table = "subscriptions"


class CustomerSubscriptionModel(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, verbose_name="User")
    subscription = models.ForeignKey(SubscriptionPlanModel, on_delete=models.SET_NULL, verbose_name="Subscription", blank=True, null=True)
    price_at_subscription = models.FloatField(verbose_name="Price After Subscription")
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date", blank=True, null=True)
    delivery_schedule = models.JSONField(verbose_name="Delivery Schedule", default=dict)
    delivery_agent = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveryAgent')

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = "customers"


class OrdersModel(BaseModel):
    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    )
    status = models.CharField(max_length=30, choices=ORDER_STATUS_CHOICES)
    schedule_date = models.DateField()
    is_morning_delivery = models.BooleanField(default=True)
    subscription = models.ForeignKey(CustomerSubscriptionModel, on_delete=models.SET_NULL, verbose_name="Subscription", blank=True, null=True)
