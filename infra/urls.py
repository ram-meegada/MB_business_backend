from infra.views import BackfillOrdersView
from django.urls import path


urlpatterns = [
    path('backfill-orders/', BackfillOrdersView.as_view(), name='backfill-orders'),
]
