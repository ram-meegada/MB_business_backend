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

    categories = list(ExpenditureCategoryModel.objects.filter(parent=None).values_list('name', flat=True))

    exp = dict(ExpenditureModel.objects
           .filter(created_at__month=timezone.now().month)
           .values('category__parent')
           .annotate(am=Cast(Sum('amount'), output_field=FloatField()))
           .values_list('category__parent__name', 'am')
           )
    res = []
    print(categories, '==========categories==============')

    colors = ['#FFC107', '#03A9F4', '#4CAF50', '#E91E63','#9C27B0', '#FF5722','#795548', '#009688','#607D8B', '#8BC34A', 'pink']
    x = 0
    for i in categories:
        print(x, '=========')
        if i in exp:
            res.append({ "name": i, "amount": exp[i], "color": colors[x], "legendFontColor": "#7F7F7F", "legendFontSize": 12 })
        else:
            res.append({ "name": i, "amount": 0, "color": colors[x], "legendFontColor": "#7F7F7F", "legendFontSize": 12 })

        x += 1

    print(res)


if __name__ == "__main__":
    main()
    pass
