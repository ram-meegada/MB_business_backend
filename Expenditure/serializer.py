from rest_framework import serializers
from Expenditure.models import ExpenditureModel


class ExpenditureWriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = ExpenditureModel
        fields = ['user', 'amount', 'category']
        extra_kwargs = {
            'amount': {
                'required': True,
                'error_messages': {'required' :'Amount is required'}
            },
            'category': {
                'required': True,
                'error_messages': {'required' :'Category is required'}
            },
        }


class ExpenditureReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenditureModel
        fields = ['id', 'amount', 'category']
