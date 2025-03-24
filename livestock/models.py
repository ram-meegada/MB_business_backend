from django.db import models
from authentication.models import UserModel
from livestock.choices import *
from authentication.models import BaseModel
from django.utils.functional import cached_property
from dateutil.relativedelta import relativedelta
from datetime import date


class LiveStockModel(BaseModel):
    image = models.ImageField(upload_to='images', blank=True, null=True)
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
    food_habits = models.TextField(blank=True)

    @cached_property
    def image_url(self):
        if self.image:
            return self.image.url
        return None

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            age = relativedelta(today, self.date_of_birth)
            return ("{} y, {} m, {} d".format(age.years, age.months, age.days))
        return None

    class Meta:
        db_table = "Live Stocks"
        ordering = ['-created_at']
