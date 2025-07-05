from rest_framework import serializers
from authentication.models import UserModel

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'name', 'phone_num', 'role', 'image']
