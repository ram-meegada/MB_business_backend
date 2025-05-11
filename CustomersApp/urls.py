from django.urls import path
from CustomersApp.views import *


urlpatterns = [
    #Customers
    path('all/', CustomersListView.as_view()),

    #Subscriptions
    path('subscriptions/all/', SubscriptionListForDropDownView.as_view()),

    #List all delivery agents
    path('delivery-agents/all/', DeliveryAgentsDropDownView.as_view()),

]
