from django.urls import path
from CustomersApp.views import *
from Analytics import PaymentAnalyticsView, MarginAnalyticsApi


urlpatterns = [
    #Customers
    path('all/', CustomersListView.as_view()),
    path('web/all/', CustomersListViewWeb.as_view()),
    path('add/', AddCustomerView.as_view()),
    path('<int:id>/', CustomerByIdView.as_view()),
    path('username-available/', CheckUsernameUniquenessView.as_view()),

    #Subscriptions
    path('subscriptions/all/', SubscriptionListForDropDownView.as_view()),

    #List all delivery agents
    path('delivery-agents/all/', DeliveryAgentsDropDownView.as_view()),

    #Payments
    path('payments/', AllPaymentsView.as_view()),
    path('view-payment/<int:id>/', PaymentByIdView.as_view()),
    path('payment-analytics/', PaymentAnalyticsView.as_view()),
    path('margin-analytics/', MarginAnalyticsApi.as_view()),

    # Orders
    path('orders/', OrdersListView.as_view()),
    path('orders/add/', AddOrdersView.as_view()),
]
