from django.db import models
from authentication.models import UserModel
from livestock.choices import *

class LiveStockModel(models.Model):
    live_stock_id = models.CharField(unique=True)
    user = models.ForeignKey(UserModel, on_delete=models.DO_NOTHING)
    breed = models.CharField(choices=breedChoices)
    is_pregnant = models.BooleanField(default=False)
    last_calvation_date = models.DateField(blank=True, null=True)
    age = models.IntegerField()
    lactation_month = models.IntegerField()
    purchase_price = models.FloatField()
    milk_capacity = models.FloatField()
    parity = models.IntegerField()
    seller_details = models.TextField(blank=True)
    qualities = models.TextField()
    food_habits = models.TextField()
