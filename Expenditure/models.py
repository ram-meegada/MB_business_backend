from django.db import models
from authentication.models import UserModel, BaseModel


class ExpenditureCategoryModel(BaseModel):
    '''
        Model for categories.
    '''
    name = models.CharField(max_length=50, unique=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="subcategories", null=True, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = "Expenditure Category"


class ExpenditureModel(BaseModel):
    '''
        Model to track business expenses.
    '''
    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(ExpenditureCategoryModel, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "Expenditure"
        ordering = ['-created_at']
