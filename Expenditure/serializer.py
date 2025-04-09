from rest_framework import serializers
from Expenditure.models import *
from utils.commonUtils import created_at_verbose


class ExpenditureWriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = ExpenditureModel
        fields = ['user', 'amount', 'category', 'description']
        extra_kwargs = {
            'amount': {
                'error_messages': {'required' :'Amount is required'}
            },
            'category': {
                'required': True,
                'error_messages': {'required' :'Category is required'}
            },
        }


class ExpenditureReadSerializer(serializers.ModelSerializer):
    sub_category = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = ExpenditureModel
        fields = ['id', 'amount', 'sub_category', 'category', 'description', 'created_at']

    def get_sub_category(self, obj):
        try:
            return obj.category.name
        except:
            return ""
    def get_category(self, obj):
        try:
            if obj.category.parent:
                return obj.category.parent.name
            return ""
        except:
            return ""
    def get_created_at(self, obj):
        try:
            return created_at_verbose(obj.created_at)
        except:
            return ""


####################### Expenditure category #####################

class ExpenditureCategorySerilaizer(serializers.ModelSerializer):
    class Meta:
        model = ExpenditureCategoryModel
        fields = ['id', 'name', 'parent']
        extra_kwargs = {
            'name': {
                'error_messages': {'required': 'Category is required'}
            }
        }
    
    def validate_name(self, value):
        if ExpenditureCategoryModel.objects.filter(name=value).exists():
            raise serializers.ValidationError("Looks like this category already added.")
        return value
