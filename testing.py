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


if __name__ == "__main__":
    check_live_Stock()
