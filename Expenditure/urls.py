from django.urls import path
from Expenditure.views import *


urlpatterns = [
    path('', ExpenditureView.as_view()),
    path('web/', ExpenditureWebView.as_view()),
    path('manage/<int:id>/', ManageExpenditureView.as_view()),
    path('analytics/', ExpenditureAnalyticsView.as_view()),

    #Category views
    path('category/', ExpenditureCategoryView.as_view()),
]
