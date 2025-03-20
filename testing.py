import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mb_backend.settings")
django.setup()


from livestock.models import *
def main():
    from utils.liveStockUtils import generate_new_live_stock_id
    l = LiveStockModel.objects.values("live_stock_id")
    print(l)


main()
