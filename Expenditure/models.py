from django.db import models
from authentication.models import UserModel, BaseModel


class ExpenditureModel(BaseModel):
    CATEGORY_CHOICES = [
        ("feed", "Feed"),
        ("medicine", "Medicine"),
        ("equipment", "Equipment"),
        ("maintenance", "Maintenance"),
        ("other", "Other")
    ]
    user = models.ForeignKey(UserModel, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    class Meta:
        db_table = "Expenditure"
        ordering = ['-created_at']
