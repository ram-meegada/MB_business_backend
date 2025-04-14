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
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    Xaxis_labels, Yaxis_values = [], []

    exp = dict(ExpenditureModel.objects
           .values("created_at__month")
           .annotate(month=Func(
               F('created_at__date'), function="TO_CHAR", template="TO_CHAR(%(expressions)s, 'Mon')"),
               total=Cast(Sum('amount'), output_field=FloatField()))
           .values_list('month', 'total'))
    
    for mon in month_names:
        value = 0
        if mon in exp:
            value = exp[mon]
        Xaxis_labels.append(mon)
        Yaxis_values.append(value)

    print(Xaxis_labels, '======')
    print(Yaxis_values, '===yyy===')
    print(len(connection.queries), '==queries===')


if __name__ == "__main__":
    main()
    pass
