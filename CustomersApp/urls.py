from django.urls import path
from CustomersApp.views import *


urlpatterns = [
    #Customers
    path('all/', CustomersListView.as_view()),
    path('web/all/', CustomersListViewWeb.as_view()),
    path('add/', AddCustomerView.as_view()),
    path('username-available/', CheckUsernameUniquenessView.as_view()),

    #Subscriptions
    path('subscriptions/all/', SubscriptionListForDropDownView.as_view()),

    #List all delivery agents
    path('delivery-agents/all/', DeliveryAgentsDropDownView.as_view()),

    #Payments
    path('payments/', AllPaymentsView.as_view()),
]
