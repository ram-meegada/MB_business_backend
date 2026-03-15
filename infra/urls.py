from infra.views import BackfillOrdersView, GetSysVersionAPI
from django.urls import path


urlpatterns = [
    path('backfill-orders/', BackfillOrdersView.as_view(), name='BackfillOrdersView'),
    path('get-sys-version/', GetSysVersionAPI.as_view(), name='GetSysVersionAPI'),
]
