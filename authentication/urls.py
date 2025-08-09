from django.urls import path
from authentication.views import *


urlpatterns = [
    path('api/token/refresh/', GenerateAccessByRefresh.as_view(), name='token_refresh'),
    path('login/', LoginView.as_view()),
    path('details/', AdminDetailsByToken.as_view()),
]
