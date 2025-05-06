from django.urls import path
from CustomersApp.views import *


urlpatterns = [
    path('all/', CustomersListView.as_view())
]