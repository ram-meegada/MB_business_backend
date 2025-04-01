import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mb_backend.settings")
django.setup()


def main():
    from livestock.models import LiveStockModel
    from utils.liveStockUtils import generate_new_live_stock_id
    l = LiveStockModel.objects.values("live_stock_id")
    print(l)


def check_live_Stock():
    from livestock.models import LiveStockModel
    l = LiveStockModel.objects.filter(is_active=False, is_deleted=True)
    print(l.values("id", "is_active", "is_deleted"))


def make_superuser():
    from authentication.models import UserModel

    u = UserModel.objects.get(username="mb5")


def generate_new_live_stock():
    from utils.liveStockUtils import generate_new_live_stock_id
    from livestock.models import LiveStockModel
    from django.db.models import Q

    # g = generate_new_live_stock_id("Bhadawari")
    # print(g)
    query = Q(live_stock_id__startswith='B')
    last_id = LiveStockModel.objects.filter(query).values("id", "live_stock_id")
    last_id = last_id.order_by("-live_stock_id")
    print(last_id.values_list('live_stock_id', 'id', 'created_at'), '-----')


def run_script_for_live_stock_id():
    from livestock.models import LiveStockModel
    from django.db.models import Value, F, CharField
    from django.db.models.functions import Concat


def exp_an():
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Q, Sum
    from Expenditure.models import ExpenditureModel

    today = timezone.now()
    q = Q(created_at__gte=(today - timedelta(days=30)), created_at__lte=today)
    ex = ExpenditureModel.objects.filter(q).aggregate(t=Sum('amount'))
    print(ex)


if __name__ == "__main__":
    exp_an()
    pass
