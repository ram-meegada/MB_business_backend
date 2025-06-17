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
        (1250, 1250),
        (1500, 1500),
        (2000, 2000),
    ]
    SCHEDULE_CHOICES = [
        (1, "Morning Only"),
        (2, "Evening only"),
        (3, "Both")
    ]
    product = models.ForeignKey(ProductsModel, on_delete=models.SET_NULL, null=True, verbose_name="Product")
    animal = models.ForeignKey(AnimalModel, on_delete=models.SET_NULL, null=True, verbose_name="Animal")
    description = models.TextField()
    price = models.FloatField(verbose_name="Morning price", blank=True, null=True)
    quantity = models.IntegerField(choices=QUANTITY_CHOICES, verbose_name="Morning quantity", blank=True, null=True)
    evening_quantity = models.IntegerField(choices=QUANTITY_CHOICES, verbose_name="Evening quantity", blank=True, null=True)
    evening_price = models.FloatField(verbose_name="Evening price", blank=True, null=True)
    schedule = models.IntegerField(choices=SCHEDULE_CHOICES, default=1)

    def __str__(self):
        if self.schedule == 1:
            return f"{quantity_verbose(self.product, self.quantity)} {self.animal} {self.product} at {self.price}/-"
        elif self.schedule == 2:
            return f"{quantity_verbose(self.product, self.evening_quantity)} {self.animal} {self.product} at {self.evening_price}/-"
        elif self.schedule == 3:
            return f"Morning {quantity_verbose(self.product, self.quantity)} {self.animal} {self.product} at {self.price}/- and Evening {quantity_verbose(self.product, self.evening_quantity)} {self.animal} {self.product} at {self.evening_price}/-"

    class Meta:
        db_table = "subscriptions"


class CustomerSubscriptionModel(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, verbose_name="User")
    subscription = models.ForeignKey(SubscriptionPlanModel, on_delete=models.SET_NULL, verbose_name="Subscription", blank=True, null=True)
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date", blank=True, null=True)
    delivery_agent = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveryAgent')

    def __str__(self):
        return str(self.pk)

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
    customer = models.ForeignKey(CustomerSubscriptionModel, on_delete=models.SET_NULL, verbose_name="Customer Subscription", blank=True, null=True)
    price_at_order = models.FloatField(verbose_name="Price at order")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['customer', 'is_morning_delivery', 'schedule_date'], name='unique_order')
        ]

    def __str__(self):
        return str(self.pk)


class MonthlyPaymentModel(models.Model):
    customer = models.ForeignKey(CustomerSubscriptionModel, on_delete=models.SET_NULL, null=True)
    month = models.DateField(help_text="Use any date in the month, e.g. 2025-06-01")
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['customer', 'month'], name='unique_monthly_payment')
        ]
