from django.urls import path
from authentication.views import *

urlpatterns = [
    path('login/', LoginView.as_view())
]
