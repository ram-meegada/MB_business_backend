from rest_framework import serializers
from livestock.models import LiveStockModel


class WriteLiveStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveStockModel
        fields = "__all__"
