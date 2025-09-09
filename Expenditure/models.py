from django.db import models
from authentication.models import UserModel
from utils.commonUtils import BaseModel


class ExpenditureCategoryModel(BaseModel):
    '''
        Model for categories.
    '''
    name = models.CharField(max_length=50)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="subcategories", null=True, blank=True)
    short_name = models.CharField(max_length=5, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = "Expenditure Category"


class ExpenditureModel(BaseModel):
    '''
        Model to track business expenses.
    '''
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(ExpenditureCategoryModel, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "Expenditure"
        ordering = ['-created_at']
