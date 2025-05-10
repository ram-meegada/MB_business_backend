from django.urls import path
from CustomersApp.views import *


urlpatterns = [
    #Customers
    path('all/', CustomersListView.as_view()),

    #Subscriptions
    path('subscriptions/all/', SubscriptionListForDropDownView.as_view()),

]
