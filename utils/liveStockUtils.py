from livestock.choices import *
from livestock.models import LiveStockModel
from django.db.models import Q


def generate_new_live_stock_id(breed):
    if breed in BUFFALO_BREEDS:
        query = Q(live_stock_id__startswith='B')
        name = "B-1"
        prefix = "B-"
    last_id = LiveStockModel.objects.filter(query).first()
    
    print(last_id.live_stock_id, '------')
    if last_id:
        suffix = int(last_id.live_stock_id.split('-')[-1])
        name = prefix + str(suffix + 1)
    return name
