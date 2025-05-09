from rest_framework import serializers
from authentication.models import UserModel

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'name', 'email', 'role']
