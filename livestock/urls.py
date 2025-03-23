from django.urls import path
from livestock.views import *

urlpatterns = [
    path("add/", AddLiveStockView.as_view()),
    path("all/", ListLiveStockView.as_view()),
    path("<int:id>/", GetLiveStockById.as_view()),
]
