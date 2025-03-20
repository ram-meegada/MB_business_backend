from django.db import models
from authentication.models import UserModel
from livestock.choices import *
from authentication.models import BaseModel


class LiveStockModel(BaseModel):
    live_stock_id = models.CharField(unique=True)
    user = models.ForeignKey(UserModel, on_delete=models.DO_NOTHING)
    breed = models.CharField(choices=breedChoices)
    is_pregnant = models.BooleanField(default=False)
    last_calvation_date = models.DateField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    lactation_month = models.IntegerField()
    purchase_price = models.FloatField()
    milk_capacity = models.FloatField()
    parity = models.IntegerField()
    seller_details = models.TextField(blank=True)
    qualities = models.TextField()
    food_habits = models.TextField()

    class Meta:
        db_table = "Live Stocks"
        ordering = ['-created_at']
