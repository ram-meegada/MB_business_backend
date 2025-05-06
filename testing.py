import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mb_backend.settings")
django.setup()

from django.db import connection, reset_queries


def main():
    from Expenditure.models import ExpenditureCategoryModel, ExpenditureModel
    from django.db.models import Prefetch
    from django.utils import timezone
    from dateutil.relativedelta import relativedelta
    from datetime import datetime
    from django.db.models import Sum, Q, F, Func, FloatField
    from django.db.models.functions import Cast
    import json
    from django.db import reset_queries, connection

    reset_queries()
    z = []
    res = ExpenditureCategoryModel.objects.filter(parent=None)
    for i in res:
        temp = {"parent": i.name}
        temp["children"] = list(ExpenditureCategoryModel.objects.filter(parent=i).values_list('name', flat=True))
        z.append(temp)
    
    print(z)

def test():
    from requests.adapters import HTTPAdapter
    from requests.sessions import Session
    import requests

    class LoggingAdapter(HTTPAdapter):
        def send(self, request, **kwargs):
            print(f"📡 Sending request to {request.url}")
            return super().send(request, **kwargs)

    print("\n=== Modern Session Logging ===")
    session = Session()
    session.mount("https://", LoggingAdapter())

    for i in range(3):
        res = session.get("https://httpbin.org/get")
        print(f"[Request {i+1}] Status: {res.status_code}")


if __name__ == "__main__":
    test()
    pass
