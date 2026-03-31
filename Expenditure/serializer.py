from rest_framework import serializers
from Expenditure.models import *
from utils.commonUtils import created_at_verbose
from django.utils import timezone


class ExpenditureWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenditureModel
        fields = ['amount', 'category', 'description']
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
    category = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = ExpenditureModel
        fields = ['id', 'amount', 'category', 'description', 'created_at']

    def get_category(self, obj):
        try:
            if obj.category.parent:
                return {
                    "id": obj.category_id,
                    "parent": obj.category.parent.name,
                    "parent_id": obj.category.parent_id,
                    "name": obj.category.name
                }
            return ""
        except:
            return ""
    def get_created_at(self, obj):
        try:
            return created_at_verbose(timezone.localtime(obj.created_at))
        except:
            return ""
        
class ExpenditureReadWebSerializer(ExpenditureReadSerializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    parent_category = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = ExpenditureModel
        fields = ['id', 'category', 'parent_category', 'amount', 'description', 'created_at']

    def get_parent_category(self, obj):
        return obj.category.parent.name

    def get_category(self, obj):
        return obj.category.name


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
