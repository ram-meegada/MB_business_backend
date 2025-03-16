from django.urls import path
from livestock.views import *

urlpatterns = [
    path("add/", AddLiveStockView.as_view())
]
