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
    from django.db.models import Sum, Q
    import json
    from django.db import reset_queries, connection

    reset_queries()

    now = timezone.now()
    present_month_first_day = now.replace(day=1)
    Q1 = Q(created_at__gte=present_month_first_day.date(), created_at__lte=now.date())
    total_expenditure = 0
    t = dict(ExpenditureModel.objects.filter(Q1)
         .values('category__parent')
         .annotate(tot=Sum('amount'))
         .values_list('category__parent__short_name', 'tot')
        )

    for v in t.values():
        total_expenditure += v

    t = {k: float(v) for k, v in t.items()}

    print(t, '===================')

    print(total_expenditure, '-----------')

    print(len(connection.queries), '==queries===')

if __name__ == "__main__":
    main()
    pass
