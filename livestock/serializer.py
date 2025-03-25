from rest_framework import serializers
from livestock.models import LiveStockModel
from utils.liveStockUtils import generate_new_live_stock_id


class WriteLiveStockSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = LiveStockModel
        fields = ['id', 'user', 'image', 'breed', 'is_pregnant', 'last_calvation_date', 'date_of_birth', 'lactation_month',
                  'purchase_price', 'milk_capacity', 'parity', 'seller_details', 'qualities', 'food_habits']
        extra_kawrgs = {"seller_details": {"default": ""},
                        "food_habits": {"default": ""}
                        }

    def validate(self, attrs):
        request = self.context.get("request")
        live_stock_id = generate_new_live_stock_id(
            request.data["breed"])
        attrs['live_stock_id'] = live_stock_id
        return super().validate(attrs)


class LiveStockListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveStockModel
        fields = ['id', 'live_stock_id', 'image_url', 'breed', 'age',
                  'milk_capacity', 'parity']


class LiveStockByIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveStockModel
        fields = ['id', 'image_url', 'breed', 'age', 'is_pregnant', 'last_calvation_date', 'date_of_birth', 'lactation_month',
                  'purchase_price', 'milk_capacity', 'parity', 'seller_details', 'qualities', 'food_habits']
