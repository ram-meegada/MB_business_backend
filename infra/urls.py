from infra.views import BackfillOrdersView, GetSysVersionAPI, PushCanonicalSkillsToDB
from django.urls import path


urlpatterns = [
    path('backfill-orders/', BackfillOrdersView.as_view(), name='BackfillOrdersView'),
    path('get-sys-version/', GetSysVersionAPI.as_view(), name='GetSysVersionAPI'),
    path('push-canonical-skills/', PushCanonicalSkillsToDB.as_view(), name='PushCanonicalSkillsToDB'),
]
