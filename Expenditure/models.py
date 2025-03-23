from django.db import models
from authentication.models import UserModel, BaseModel


class ExpenditureModel(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.DO_NOTHING)
    amount = models.IntegerField()
    
