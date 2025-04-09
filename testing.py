import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mb_backend.settings")
django.setup()

from django.db import connection, reset_queries


def main():
    from Expenditure.models import ExpenditureCategoryModel
    from django.db.models import Prefetch

    data = []
    # reset_queries()
    print(len(connection.queries), '----starting----')
    exp = (ExpenditureCategoryModel.objects.filter(parent=None)
            .prefetch_related('subcategories'))
    for i in exp:
        data.append({"label": i.name, "value": i.name, "isHeader": True})
        for j in i.subcategories.all():
            data.append({"label": j.name, 'value': j.name})

    import json

    d = json.dumps(data, indent=4)
    print(d)
    print(len(connection.queries), '--------------------queries-----------')

if __name__ == "__main__":
    main()
    pass
